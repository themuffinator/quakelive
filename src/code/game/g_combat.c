/*
===========================================================================
Copyright (C) 1999-2005 Id Software, Inc.

This file is part of Quake III Arena source code.

Quake III Arena source code is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Quake III Arena source code is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
===========================================================================
*/
//
// g_combat.c

#include "g_local.h"
#include <limits.h>

#define COMPLAINT_PROMPT_MSEC	15500
#define COMPLAINT_DECAY_MSEC	15500

/*
=============
G_ComplaintResetClient

Clears the complaint bookkeeping attached to a client. When resetCount is true the lifetime
complaint counter is also zeroed.
=============
*/
void G_ComplaintResetClient( gclient_t *client, qboolean resetCount ) {
	if ( !client ) {
		return;
	}

	client->complaintClient = -1;
	client->complaintEndTime = 0;
	client->complaintTarget = -1;
	client->complaintDamage = 0;
	client->complaintLastDamageTime = 0;

	if ( resetCount ) {
		client->complaintCount = 0;
	}
}

/*
=============
G_ComplaintConsiderForDamage

Accumulates team damage dealt by an attacker and prompts the victim once the configured
threshold is exceeded.
=============
*/
void G_ComplaintConsiderForDamage( gentity_t *attacker, gentity_t *victim, int damage ) {
	gclient_t *attackerClient;
	gclient_t *victimClient;
	int threshold;

	if ( damage <= 0 || !attacker || !victim ) {
		return;
	}

	attackerClient = attacker->client;
	victimClient = victim->client;

	if ( !attackerClient || !victimClient ) {
		return;
	}

	if ( attackerClient->pers.connected != CON_CONNECTED ) {
		return;
	}

	if ( attackerClient == victimClient ) {
		return;
	}

	if ( attackerClient->sess.sessionTeam != victimClient->sess.sessionTeam ) {
		return;
	}

	if ( attackerClient->sess.sessionTeam == TEAM_SPECTATOR ) {
		return;
	}

	threshold = g_complaintDamageThreshold.integer;
	if ( threshold <= 0 ) {
		return;
	}

	if ( attackerClient->complaintTarget != victim->s.number ) {
		attackerClient->complaintTarget = victim->s.number;
		attackerClient->complaintDamage = 0;
	}

	if ( attackerClient->complaintLastDamageTime > 0 && level.time - attackerClient->complaintLastDamageTime > COMPLAINT_DECAY_MSEC ) {
		attackerClient->complaintDamage = 0;
	}

	attackerClient->complaintLastDamageTime = level.time;

	if ( damage > INT_MAX - attackerClient->complaintDamage ) {
		attackerClient->complaintDamage = INT_MAX;
	} else {
		attackerClient->complaintDamage += damage;
	}

	if ( attackerClient->complaintDamage < threshold ) {
		return;
	}

	if ( victimClient->complaintClient >= 0 && victimClient->complaintEndTime > level.time ) {
		attackerClient->complaintDamage = 0;
		attackerClient->complaintTarget = -1;
		return;
	}

	if ( attackerClient->sess.sessionTeam == TEAM_SPECTATOR ) {
		trap_SendServerCommand( victim - g_entities, "complaint -4" );
		attackerClient->complaintDamage = 0;
		attackerClient->complaintTarget = -1;
		return;
	}

	victimClient->complaintClient = attacker->s.number;
	victimClient->complaintEndTime = level.time + COMPLAINT_PROMPT_MSEC;
	trap_SendServerCommand( victim - g_entities, va( "complaint %i", attacker->s.number ) );

	attackerClient->complaintDamage = 0;
	attackerClient->complaintTarget = -1;
}

/*
=============
G_ComplaintResolve

Finalises a pending complaint, applying either the punishment or forgiveness flow
for the attacker and informing both parties of the outcome.
=============
*/
void G_ComplaintResolve( gentity_t *victim, qboolean filed ) {
	gclient_t *victimClient;
	gentity_t *attacker;
	gclient_t *attackerClient;
	int attackerNum;
	int victimNum;

	if ( !victim || !victim->client ) {
		return;
	}

	victimClient = victim->client;
	victimNum = victim - g_entities;
	attackerNum = victimClient->complaintClient;
	victimClient->complaintClient = -1;
	victimClient->complaintEndTime = 0;

	if ( attackerNum < 0 || attackerNum >= level.maxclients ) {
		trap_SendServerCommand( victimNum, "complaint -3" );
		return;
	}

	attacker = g_entities + attackerNum;
	attackerClient = attacker->client;

	if ( !attackerClient || attackerClient->pers.connected != CON_CONNECTED ) {
		trap_SendServerCommand( victimNum, "complaint -3" );
		return;
	}

	attackerClient->complaintDamage = 0;
	attackerClient->complaintTarget = -1;
	attackerClient->complaintLastDamageTime = 0;

	if ( filed ) {
		attackerClient->complaintCount++;
		trap_SendServerCommand( attackerNum, "print \"^1Warning^7: Complaint filed against you.\n\"" );
		trap_SendServerCommand( victimNum, "complaint -1" );

		if ( g_complaintLimit.integer > 0 && attackerClient->complaintCount >= g_complaintLimit.integer ) {
			trap_DropClient( attackerNum, "kicked after too many complaints." );
		}
	} else {
		trap_SendServerCommand( attackerNum, "print \"No complaint filed against you.\n\"" );
		trap_SendServerCommand( victimNum, "complaint -2" );
	}
}

/*
=============
G_ComplaintClientDisconnected

Clears any outstanding complaint state that references a departing client and
notifies victims that the complaint is no longer actionable.
=============
*/
void G_ComplaintClientDisconnected( int clientNum ) {
	int i;

	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return;
	}

	for ( i = 0; i < level.maxclients; ++i ) {
		gclient_t *client = level.clients + i;

		if ( client->complaintClient == clientNum ) {
			client->complaintClient = -1;
			client->complaintEndTime = 0;
			trap_SendServerCommand( i, "complaint -3" );
		}

		if ( client->complaintTarget == clientNum ) {
			client->complaintTarget = -1;
			client->complaintDamage = 0;
			client->complaintLastDamageTime = 0;
		}
	}
}

/*
============
ScorePlum
============
*/
void ScorePlum( gentity_t *ent, vec3_t origin, int score ) {
	gentity_t *plum;

	if ( !g_damagePlums.integer ) {
		return;
	}

	plum = G_TempEntity( origin, EV_SCOREPLUM );
	// only send this temp entity to a single client
	plum->r.svFlags |= SVF_SINGLECLIENT;
	plum->r.singleClient = ent->s.number;
	//
	plum->s.otherEntityNum = ent->s.number;
	plum->s.time = score;
}

/*
============
AddScore

Adds score to both the client and his team
============
*/
void AddScore( gentity_t *ent, vec3_t origin, int score ) {
	if ( !ent->client ) {
		return;
	}
	// no scoring during pre-match warmup
	if ( level.warmupTime ) {
		return;
	}

	if ( ent->client->scoreModifier > 0.0f && ent->client->scoreModifier != 1.0f ) {
		float	scaled;
		int		resolved;

		scaled = (float)score * ent->client->scoreModifier;
		if ( scaled > 0.0f ) {
			resolved = (int)( scaled + 0.5f );
			if ( resolved < 1 ) {
				resolved = 1;
			}
		} else if ( scaled < 0.0f ) {
			resolved = (int)( scaled - 0.5f );
			if ( resolved > -1 ) {
				resolved = -1;
			}
		} else {
			resolved = 0;
		}

		score = resolved;
	}
	// show score plum
	ScorePlum(ent, origin, score);
	//
	ent->client->ps.persistant[PERS_SCORE] += score;
	if ( g_gametype.integer == GT_TEAM )
		level.teamScores[ ent->client->ps.persistant[PERS_TEAM] ] += score;
	CalculateRanks();
}
/*
=============
G_CalcPowerupDamageScale

Returns the total powerup-based damage multiplier for the attacker.
=============
*/
static float G_CalcPowerupDamageScale( gentity_t *attacker ) {
	float		scale;

	scale = 1.0f;
	if ( !attacker || !attacker->client ) {
		return scale;
	}

	if ( attacker->client->ps.powerups[PW_QUAD] ) {
		scale *= g_weaponConfig.quadDamageMultiplier;
	}

	if ( attacker->client->persistantPowerup && attacker->client->persistantPowerup->item && attacker->client->persistantPowerup->item->giTag == PW_DOUBLER ) {
		scale *= 2.0f;
	}

	return scale;
}
/*
=============
G_IsRailgunHeadshot

Determines if the supplied impact point resides in the head region of the target.
=============
*/
static qboolean G_IsRailgunHeadshot( gentity_t *targ, vec3_t point ) {
	float	headThreshold;
	float	height;

	if ( !targ || !targ->client || !point ) {
		return qfalse;
	}

	height = targ->r.maxs[2] - targ->r.mins[2];
	if ( height <= 0.0f ) {
		return qfalse;
	}

	headThreshold = targ->r.currentOrigin[2] + targ->r.maxs[2] - ( height * 0.25f );
	return point[2] >= headThreshold;
}
/*
=============
G_ClampModDamage

Clamps weapon damage against the active weapon configuration when CVars change mid-match.
=============
*/
static int G_ClampModDamage( int damage, int mod, gentity_t *attacker ) {
	int		configuredDamage;

	configuredDamage = 0;
	(void)attacker;
	switch ( mod ) {
	case MOD_GAUNTLET:
		configuredDamage = g_weaponConfig.gauntletDamage;
		break;
	case MOD_MACHINEGUN:
		configuredDamage = ( g_gametype.integer != GT_TEAM ) ? g_weaponConfig.machinegunDamage : g_weaponConfig.machinegunTeamDamage;
		break;
	case MOD_HMG:
		configuredDamage = g_weaponConfig.heavyMachinegunDamage;
		break;
	case MOD_SHOTGUN:
		configuredDamage = g_weaponConfig.shotgunDamage;
		break;
	case MOD_GRENADE:
		configuredDamage = g_weaponConfig.grenadeDamage;
		break;
	case MOD_GRENADE_SPLASH:
		configuredDamage = g_weaponConfig.grenadeSplashDamage;
		break;
	case MOD_ROCKET:
		configuredDamage = g_weaponConfig.rocketDamage;
		break;
	case MOD_ROCKET_SPLASH:
		configuredDamage = g_weaponConfig.rocketSplashDamage;
		break;
	case MOD_PLASMA:
		configuredDamage = g_weaponConfig.plasmaDamage;
		break;
	case MOD_PLASMA_SPLASH:
		configuredDamage = g_weaponConfig.plasmaSplashDamage;
		break;
	case MOD_RAILGUN:
	case MOD_RAILGUN_HEADSHOT:
		configuredDamage = g_weaponConfig.railgunDamage;
		break;
	case MOD_LIGHTNING:
	case MOD_LIGHTNING_DISCHARGE:
		configuredDamage = g_weaponConfig.lightningDamage;
		break;
	case MOD_BFG:
		configuredDamage = g_weaponConfig.bfgDamage;
		break;
	case MOD_BFG_SPLASH:
		configuredDamage = g_weaponConfig.bfgSplashDamage;
		break;
	case MOD_PROXIMITY_MINE:
		configuredDamage = g_weaponConfig.proximityLauncherDamage;
		break;
	default:
		break;
	}

	if ( configuredDamage > 0 && damage > configuredDamage ) {
		return configuredDamage;
	}

	return damage;
}
/*
=============
G_BattleSuitDamageScale

Returns the active damage scale applied when the Battlesuit powerup is running.
=============
*/
static float G_BattleSuitDamageScale( void ) {
	float	scale;

	scale = g_battleSuitDampen.value;
	if ( scale <= 0.0f ) {
		scale = 0.5f;
	} else if ( scale > 1.0f ) {
		scale = 1.0f;
	}

	return scale;
}



/*
=================
TossClientItems

Toss the weapon and powerups for the specified player using the configured flag rules.
=================
*/
void TossClientItems( gentity_t *self, gentity_t *attacker, flagDropContext_t context, int meansOfDeath ) {
	gitem_t		*item;
	int			weapon;
	float		angle;
	int			i;
	gentity_t		*drop;

	// drop the weapon if not a gauntlet or machinegun
	weapon = self->s.weapon;

	// make a special check to see if they are changing to a new
	// weapon that isn't the mg or gauntlet.  Without this, a client
	// can pick up a weapon, be killed, and not drop the weapon because
	// their weapon change hasn't completed yet and they are still holding the MG.
	if ( weapon == WP_MACHINEGUN || weapon == WP_GRAPPLING_HOOK ) {
		if ( self->client->ps.weaponstate == WEAPON_DROPPING ) {
			weapon = self->client->pers.cmd.weapon;
		}
		if ( !( self->client->ps.stats[STAT_WEAPONS] & ( 1 << weapon ) ) ) {
			weapon = WP_NONE;
		}
	}

	if ( weapon > WP_MACHINEGUN && weapon != WP_GRAPPLING_HOOK &&
		self->client->ps.ammo[ weapon ] ) {
		// find the item type for this weapon
		item = BG_FindItemForWeapon( weapon );

		// spawn the item
		Drop_Item( self, item, 0 );
	}

	// drop all the powerups if not in teamplay
	if ( g_gametype.integer != GT_TEAM ) {
		angle = 45;
		for ( i = 1 ; i < PW_NUM_POWERUPS ; i++ ) {
			if ( i == PW_NEUTRALFLAG || i == PW_REDFLAG || i == PW_BLUEFLAG ) {
				continue;
			}
			if ( self->client->ps.powerups[ i ] > level.time ) {
				item = BG_FindItemForPowerup( i );
				if ( !item ) {
					continue;
				}
				drop = Drop_Item( self, item, angle );
				if ( drop ) {
					// decide how many seconds it has left
					drop->count = ( self->client->ps.powerups[ i ] - level.time ) / 1000;
					if ( drop->count < 1 ) {
						drop->count = 1;
					}
				}
				angle += 45;
			}
		}
	}

	G_TossFlag( self, PW_NEUTRALFLAG, context, attacker, meansOfDeath, NULL );
	G_TossFlag( self, PW_REDFLAG, context, attacker, meansOfDeath, NULL );
	G_TossFlag( self, PW_BLUEFLAG, context, attacker, meansOfDeath, NULL );
}

/*
=================
TossClientCubes
=================
*/
extern gentity_t	*neutralObelisk;

void TossClientCubes( gentity_t *self ) {
	gitem_t		*item;
	gentity_t	*drop;
	vec3_t		velocity;
	vec3_t		angles;
	vec3_t		origin;

	self->client->ps.generic1 = 0;

	// this should never happen but we should never
	// get the server to crash due to skull being spawned in
	if (!G_EntitiesFree()) {
		return;
	}

	if( self->client->sess.sessionTeam == TEAM_RED ) {
		item = BG_FindItem( "Red Cube" );
	}
	else {
		item = BG_FindItem( "Blue Cube" );
	}

	angles[YAW] = (float)(level.time % 360);
	angles[PITCH] = 0;	// always forward
	angles[ROLL] = 0;

	AngleVectors( angles, velocity, NULL, NULL );
	VectorScale( velocity, 150, velocity );
	velocity[2] += 200 + crandom() * 50;

	if( neutralObelisk ) {
		VectorCopy( neutralObelisk->s.pos.trBase, origin );
		origin[2] += 44;
	} else {
		VectorClear( origin ) ;
	}

	drop = LaunchItem( item, origin, velocity );

	drop->nextthink = level.time + g_cubeTimeout.integer * 1000;
	drop->think = G_FreeEntity;
	drop->spawnflags = self->client->sess.sessionTeam;
}


/*
=================
TossClientPersistantPowerups
=================
*/
void TossClientPersistantPowerups( gentity_t *ent ) {
	gentity_t	*powerup;

	if( !ent->client ) {
		return;
	}

	if( !ent->client->persistantPowerup ) {
		return;
	}

	powerup = ent->client->persistantPowerup;

	powerup->r.svFlags &= ~SVF_NOCLIENT;
	powerup->s.eFlags &= ~EF_NODRAW;
	powerup->r.contents = CONTENTS_TRIGGER;
	trap_LinkEntity( powerup );

	ent->client->ps.stats[STAT_PERSISTANT_POWERUP] = 0;
	ent->client->persistantPowerup = NULL;
}


/*
==================
LookAtKiller
==================
*/
void LookAtKiller( gentity_t *self, gentity_t *inflictor, gentity_t *attacker ) {
	vec3_t		dir;
	vec3_t		angles;

	if ( attacker && attacker != self ) {
		VectorSubtract (attacker->s.pos.trBase, self->s.pos.trBase, dir);
	} else if ( inflictor && inflictor != self ) {
		VectorSubtract (inflictor->s.pos.trBase, self->s.pos.trBase, dir);
	} else {
		self->client->ps.stats[STAT_DEAD_YAW] = self->s.angles[YAW];
		return;
	}

	self->client->ps.stats[STAT_DEAD_YAW] = vectoyaw ( dir );

	angles[YAW] = vectoyaw ( dir );
	angles[PITCH] = 0; 
	angles[ROLL] = 0;
}

/*
==================
GibEntity
==================
*/
void GibEntity( gentity_t *self, int killer ) {
	gentity_t *ent;
	int i;

	//if this entity still has kamikaze
	if (self->s.eFlags & EF_KAMIKAZE) {
		// check if there is a kamikaze timer around for this owner
		for (i = 0; i < MAX_GENTITIES; i++) {
			ent = &g_entities[i];
			if (!ent->inuse)
				continue;
			if (ent->activator != self)
				continue;
			if (strcmp(ent->classname, "kamikaze timer"))
				continue;
			G_FreeEntity(ent);
			break;
		}
	}
	G_AddEvent( self, EV_GIB_PLAYER, killer );
	self->takedamage = qfalse;
	self->s.eType = ET_INVISIBLE;
	self->r.contents = 0;
}

/*
==================
body_die
==================
*/
void body_die( gentity_t *self, gentity_t *inflictor, gentity_t *attacker, int damage, int meansOfDeath ) {
	if ( self->health > GIB_HEALTH ) {
		return;
	}
	if ( !g_blood.integer ) {
		self->health = GIB_HEALTH+1;
		return;
	}

	GibEntity( self, 0 );
}


// these are just for logging, the client prints its own messages
char	*modNames[] = {
	"MOD_UNKNOWN",
	"MOD_SHOTGUN",
	"MOD_GAUNTLET",
	"MOD_MACHINEGUN",
	"MOD_GRENADE",
	"MOD_GRENADE_SPLASH",
	"MOD_ROCKET",
	"MOD_ROCKET_SPLASH",
	"MOD_PLASMA",
	"MOD_PLASMA_SPLASH",
	"MOD_RAILGUN",
	"MOD_LIGHTNING",
	"MOD_BFG",
	"MOD_BFG_SPLASH",
	"MOD_WATER",
	"MOD_SLIME",
	"MOD_LAVA",
	"MOD_CRUSH",
	"MOD_TELEFRAG",
	"MOD_FALLING",
	"MOD_SUICIDE",
	"MOD_TARGET_LASER",
	"MOD_TRIGGER_HURT",
	"MOD_NAIL",
	"MOD_CHAINGUN",
	"MOD_PROXIMITY_MINE",
	"MOD_KAMIKAZE",
        "MOD_JUICED",
        "MOD_GRAPPLE",
        "MOD_SWITCHTEAM",
        "MOD_THAW",
        "MOD_LIGHTNING_DISCHARGE",
        "MOD_HMG",
        "MOD_RAILGUN_HEADSHOT"
};

/*
==================
Kamikaze_DeathActivate
==================
*/
void Kamikaze_DeathActivate( gentity_t *ent ) {
	G_StartKamikaze(ent);
	G_FreeEntity(ent);
}

/*
==================
Kamikaze_DeathTimer
==================
*/
void Kamikaze_DeathTimer( gentity_t *self ) {
	gentity_t *ent;

	ent = G_Spawn();
	ent->classname = "kamikaze timer";
	VectorCopy(self->s.pos.trBase, ent->s.pos.trBase);
	ent->r.svFlags |= SVF_NOCLIENT;
	ent->think = Kamikaze_DeathActivate;
	ent->nextthink = level.time + 5 * 1000;

	ent->activator = self;
}


/*
==================
CheckAlmostCapture
==================
*/
void CheckAlmostCapture( gentity_t *self, gentity_t *attacker ) {
	gentity_t	*ent;
	vec3_t		dir;
	char		*classname;

	// if this player was carrying a flag
	if ( self->client->ps.powerups[PW_REDFLAG] ||
		self->client->ps.powerups[PW_BLUEFLAG] ||
		self->client->ps.powerups[PW_NEUTRALFLAG] ) {
		// get the goal flag this player should have been going for
		if ( g_gametype.integer == GT_CTF ) {
			if ( self->client->sess.sessionTeam == TEAM_BLUE ) {
				classname = "team_CTF_blueflag";
			}
			else {
				classname = "team_CTF_redflag";
			}
		}
		else {
			if ( self->client->sess.sessionTeam == TEAM_BLUE ) {
				classname = "team_CTF_redflag";
			}
			else {
				classname = "team_CTF_blueflag";
			}
		}
		ent = NULL;
		do
		{
			ent = G_Find(ent, FOFS(classname), classname);
		} while (ent && (ent->flags & FL_DROPPED_ITEM));
		// if we found the destination flag and it's not picked up
		if (ent && !(ent->r.svFlags & SVF_NOCLIENT) ) {
			// if the player was *very* close
			VectorSubtract( self->client->ps.origin, ent->s.origin, dir );
			if ( VectorLength(dir) < 200 ) {
				self->client->ps.persistant[PERS_PLAYEREVENTS] ^= PLAYEREVENT_HOLYSHIT;
				if ( attacker->client ) {
					attacker->client->ps.persistant[PERS_PLAYEREVENTS] ^= PLAYEREVENT_HOLYSHIT;
				}
			}
		}
	}
}

/*
==================
CheckAlmostScored
==================
*/
void CheckAlmostScored( gentity_t *self, gentity_t *attacker ) {
	gentity_t	*ent;
	vec3_t		dir;
	char		*classname;

	// if the player was carrying cubes
	if ( self->client->ps.generic1 ) {
		if ( self->client->sess.sessionTeam == TEAM_BLUE ) {
			classname = "team_redobelisk";
		}
		else {
			classname = "team_blueobelisk";
		}
		ent = G_Find(NULL, FOFS(classname), classname);
		// if we found the destination obelisk
		if ( ent ) {
			// if the player was *very* close
			VectorSubtract( self->client->ps.origin, ent->s.origin, dir );
			if ( VectorLength(dir) < 200 ) {
				self->client->ps.persistant[PERS_PLAYEREVENTS] ^= PLAYEREVENT_HOLYSHIT;
				if ( attacker->client ) {
					attacker->client->ps.persistant[PERS_PLAYEREVENTS] ^= PLAYEREVENT_HOLYSHIT;
				}
			}
		}
	}
}

/*
==================
player_die
==================
*/
void player_die( gentity_t *self, gentity_t *inflictor, gentity_t *attacker, int damage, int meansOfDeath ) {
	gentity_t	*ent;
	int			anim;
	int			contents;
	int			killer;
	int			i;
	char		*killerName, *obit;

	if ( G_FreezeHandlePlayerDeath( self, inflictor, attacker, damage, meansOfDeath ) ) {
		return;
	}

	if ( self->client->ps.pm_type == PM_DEAD ) {
		return;
	}

	if ( level.intermissiontime ) {
		return;
	}

	// check for an almost capture
	CheckAlmostCapture( self, attacker );
	// check for a player that almost brought in cubes
	CheckAlmostScored( self, attacker );

	if (self->client && self->client->hook) {
		Weapon_HookFree(self->client->hook);
	}
	if ((self->client->ps.eFlags & EF_TICKING) && self->activator) {
		self->client->ps.eFlags &= ~EF_TICKING;
		self->activator->think = G_FreeEntity;
		self->activator->nextthink = level.time;
	}
	self->client->ps.pm_type = PM_DEAD;

	if ( attacker ) {
		killer = attacker->s.number;
		if ( attacker->client ) {
			killerName = attacker->client->pers.netname;
		} else {
			killerName = "<non-client>";
		}
	} else {
		killer = ENTITYNUM_WORLD;
		killerName = "<world>";
	}

	if ( killer < 0 || killer >= MAX_CLIENTS ) {
		killer = ENTITYNUM_WORLD;
		killerName = "<world>";
	}

	if ( meansOfDeath < 0 || meansOfDeath >= sizeof( modNames ) / sizeof( modNames[0] ) ) {
		obit = "<bad obituary>";
	} else {
		obit = modNames[ meansOfDeath ];
	}

	G_LogPrintf("Kill: %i %i %i: %s killed %s by %s\n", 
		killer, self->s.number, meansOfDeath, killerName, 
		self->client->pers.netname, obit );

	// broadcast the death event to everyone
	ent = G_TempEntity( self->r.currentOrigin, EV_OBITUARY );
	ent->s.eventParm = meansOfDeath;
	ent->s.otherEntityNum = self->s.number;
	ent->s.otherEntityNum2 = killer;
	ent->r.svFlags = SVF_BROADCAST;	// send to everyone

	self->enemy = attacker;

	self->client->ps.persistant[PERS_KILLED]++;

	if (attacker && attacker->client) {
		attacker->client->lastkilled_client = self->s.number;

		if ( attacker == self || OnSameTeam (self, attacker ) ) {
			AddScore( attacker, self->r.currentOrigin, -1 );
		} else {
			AddScore( attacker, self->r.currentOrigin, 1 );
			G_ADAwardBonus( attacker, self->r.currentOrigin, g_adElimScoreBonus.integer, S_COLOR_YELLOW "Elimination bonus" );

			if( meansOfDeath == MOD_GAUNTLET ) {
				
				// play humiliation on player
				attacker->client->ps.persistant[PERS_GAUNTLET_FRAG_COUNT]++;

				// add the sprite over the player's head
				attacker->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
				attacker->client->ps.eFlags |= EF_AWARD_GAUNTLET;
				attacker->client->rewardTime = level.time + REWARD_SPRITE_TIME;

				// also play humiliation on target
				self->client->ps.persistant[PERS_PLAYEREVENTS] ^= PLAYEREVENT_GAUNTLETREWARD;
			}

			// check for two kills in a short amount of time
			// if this is close enough to the last kill, give a reward sound
			if ( level.time - attacker->client->lastKillTime < CARNAGE_REWARD_TIME ) {
				// play excellent on player
				attacker->client->ps.persistant[PERS_EXCELLENT_COUNT]++;

				// add the sprite over the player's head
				attacker->client->ps.eFlags &= ~(EF_AWARD_IMPRESSIVE | EF_AWARD_EXCELLENT | EF_AWARD_GAUNTLET | EF_AWARD_ASSIST | EF_AWARD_DEFEND | EF_AWARD_CAP );
				attacker->client->ps.eFlags |= EF_AWARD_EXCELLENT;
				attacker->client->rewardTime = level.time + REWARD_SPRITE_TIME;
			}
			attacker->client->lastKillTime = level.time;

		}
	} else {
		AddScore( self, self->r.currentOrigin, -1 );
	}

	// Add team bonuses
	Team_FragBonuses(self, inflictor, attacker);
	G_RRHandlePlayerDeath( self, attacker );

	// if client is in a nodrop area, don't drop anything (but return CTF flags!)
	contents = trap_PointContents( self->r.currentOrigin, -1 );
	if ( !( contents & CONTENTS_NODROP )) {
		TossClientItems( self, attacker, FLAG_DROP_CONTEXT_DEATH, meansOfDeath );
		G_DropClientKeys( self );
	}
	else {
		G_TossFlag( self, PW_NEUTRALFLAG, FLAG_DROP_CONTEXT_FORCED_RETURN, attacker, meansOfDeath, NULL );
		G_TossFlag( self, PW_REDFLAG, FLAG_DROP_CONTEXT_FORCED_RETURN, attacker, meansOfDeath, NULL );
		G_TossFlag( self, PW_BLUEFLAG, FLAG_DROP_CONTEXT_FORCED_RETURN, attacker, meansOfDeath, NULL );
		self->keyMask = 0;
	}
	TossClientPersistantPowerups( self );
	if( g_gametype.integer == GT_HARVESTER ) {
		TossClientCubes( self );
	}

	Cmd_Score_f( self );		// show scores
	// send updated scores to any clients that are following this one,
	// or they would get stale scoreboards
	for ( i = 0 ; i < level.maxclients ; i++ ) {
		gclient_t	*client;

		client = &level.clients[i];
		if ( client->pers.connected != CON_CONNECTED ) {
			continue;
		}
		if ( client->sess.sessionTeam != TEAM_SPECTATOR ) {
			continue;
		}
		if ( client->sess.spectatorClient == self->s.number ) {
			Cmd_Score_f( g_entities + i );
		}
	}

	self->takedamage = qtrue;	// can still be gibbed

	self->s.weapon = WP_NONE;
	self->s.powerups = 0;
	self->r.contents = CONTENTS_CORPSE;

	self->s.angles[0] = 0;
	self->s.angles[2] = 0;
	LookAtKiller (self, inflictor, attacker);

	VectorCopy( self->s.angles, self->client->ps.viewangles );

	self->s.loopSound = 0;

	self->r.maxs[2] = -8;

	// don't allow respawn until the death anim is done
	// g_forcerespawn may force spawning at some later time
	{
		int respawnDelay = 1700;
		if ( level.suddenDeathActive ) {
			int suddenDeathDelay = G_GetSuddenDeathRespawnDelay();
			if ( suddenDeathDelay < 0 ) {
				self->client->respawnTime = INT_MAX;
			} else {
				if ( suddenDeathDelay < respawnDelay ) {
					suddenDeathDelay = respawnDelay;
				}
				self->client->respawnTime = level.time + suddenDeathDelay;
			}
		} else {
			self->client->respawnTime = level.time + respawnDelay;
		}
	}

	// remove powerups
	memset( self->client->ps.powerups, 0, sizeof(self->client->ps.powerups) );

	// never gib in a nodrop
	if ( (self->health <= GIB_HEALTH && !(contents & CONTENTS_NODROP) && g_blood.integer) || meansOfDeath == MOD_SUICIDE) {
		// gib death
		GibEntity( self, killer );
	} else {
		// normal death
		static int i;

		switch ( i ) {
		case 0:
			anim = BOTH_DEATH1;
			break;
		case 1:
			anim = BOTH_DEATH2;
			break;
		case 2:
		default:
			anim = BOTH_DEATH3;
			break;
		}

		// for the no-blood option, we need to prevent the health
		// from going to gib level
		if ( self->health <= GIB_HEALTH ) {
			self->health = GIB_HEALTH+1;
		}

		self->client->ps.legsAnim = 
			( ( self->client->ps.legsAnim & ANIM_TOGGLEBIT ) ^ ANIM_TOGGLEBIT ) | anim;
		self->client->ps.torsoAnim = 
			( ( self->client->ps.torsoAnim & ANIM_TOGGLEBIT ) ^ ANIM_TOGGLEBIT ) | anim;

		G_AddEvent( self, EV_DEATH1 + i, killer );

		// the body can still be gibbed
		self->die = body_die;

		// globally cycle through the different death animations
		i = ( i + 1 ) % 3;

		if (self->s.eFlags & EF_KAMIKAZE) {
			Kamikaze_DeathTimer( self );
		}
	}

	trap_LinkEntity (self);

}


/*
================
CheckArmor
================
*/
int CheckArmor (gentity_t *ent, int damage, int dflags)
{
	gclient_t	*client;
	int			save;
	int			count;

	if (!damage)
		return 0;

	client = ent->client;

	if (!client)
		return 0;

	if (dflags & DAMAGE_NO_ARMOR)
		return 0;

	// armor
	count = client->ps.stats[STAT_ARMOR];
	save = ceil( damage * ARMOR_PROTECTION );
	if (save >= count)
		save = count;

	if (!save)
		return 0;

	client->ps.stats[STAT_ARMOR] -= save;

	return save;
}

/*
================
RaySphereIntersections
================
*/
int RaySphereIntersections( vec3_t origin, float radius, vec3_t point, vec3_t dir, vec3_t intersections[2] ) {
	float b, c, d, t;

	//	| origin - (point + t * dir) | = radius
	//	a = dir[0]^2 + dir[1]^2 + dir[2]^2;
	//	b = 2 * (dir[0] * (point[0] - origin[0]) + dir[1] * (point[1] - origin[1]) + dir[2] * (point[2] - origin[2]));
	//	c = (point[0] - origin[0])^2 + (point[1] - origin[1])^2 + (point[2] - origin[2])^2 - radius^2;

	// normalize dir so a = 1
	VectorNormalize(dir);
	b = 2 * (dir[0] * (point[0] - origin[0]) + dir[1] * (point[1] - origin[1]) + dir[2] * (point[2] - origin[2]));
	c = (point[0] - origin[0]) * (point[0] - origin[0]) +
		(point[1] - origin[1]) * (point[1] - origin[1]) +
		(point[2] - origin[2]) * (point[2] - origin[2]) -
		radius * radius;

	d = b * b - 4 * c;
	if (d > 0) {
		t = (- b + sqrt(d)) / 2;
		VectorMA(point, t, dir, intersections[0]);
		t = (- b - sqrt(d)) / 2;
		VectorMA(point, t, dir, intersections[1]);
		return 2;
	}
	else if (d == 0) {
		t = (- b ) / 2;
		VectorMA(point, t, dir, intersections[0]);
		return 1;
	}
	return 0;
}

/*
================
G_InvulnerabilityEffect
================
*/
int G_InvulnerabilityEffect( gentity_t *targ, vec3_t dir, vec3_t point, vec3_t impactpoint, vec3_t bouncedir ) {
	gentity_t	*impact;
	vec3_t		intersections[2], vec;
	int			n;

	if ( !targ->client ) {
		return qfalse;
	}
	VectorCopy(dir, vec);
	VectorInverse(vec);
	// sphere model radius = 42 units
	n = RaySphereIntersections( targ->client->ps.origin, 42, point, vec, intersections);
	if (n > 0) {
		impact = G_TempEntity( targ->client->ps.origin, EV_INVUL_IMPACT );
		VectorSubtract(intersections[0], targ->client->ps.origin, vec);
		vectoangles(vec, impact->s.angles);
		impact->s.angles[0] += 90;
		if (impact->s.angles[0] > 360)
			impact->s.angles[0] -= 360;
		if ( impactpoint ) {
			VectorCopy( intersections[0], impactpoint );
		}
		if ( bouncedir ) {
			VectorCopy( vec, bouncedir );
			VectorNormalize( bouncedir );
		}
		return qtrue;
	}
	else {
		return qfalse;
	}
}
/*
============
T_Damage

targ		entity that is being damaged
inflictor	entity that is causing the damage
attacker	entity that caused the inflictor to damage targ
	example: targ=monster, inflictor=rocket, attacker=player

dir			direction of the attack for knockback
point		point at which the damage is being inflicted, used for headshots
damage		amount of damage being inflicted
knockback	force to be applied against targ as a result of the damage

inflictor, attacker, dir, and point can be NULL for environmental effects

dflags		these flags are used to control how T_Damage works
	DAMAGE_RADIUS			damage was indirect (from a nearby explosion)
	DAMAGE_NO_ARMOR			armor does not protect from this damage
	DAMAGE_NO_KNOCKBACK		do not affect velocity, just view angles
	DAMAGE_NO_PROTECTION	kills godmode, armor, everything
============
*/

static float G_KnockbackScaleForMOD( int mod, qboolean selfInflicted ) {
        switch ( mod ) {
        case MOD_GAUNTLET:
                return g_knockbackConfig.gauntlet;
        case MOD_MACHINEGUN:
                return g_knockbackConfig.machinegun;
        case MOD_HMG:
                return g_knockbackConfig.heavyMachinegun;
        case MOD_SHOTGUN:
                return g_knockbackConfig.shotgun;
        case MOD_GRENADE:
        case MOD_GRENADE_SPLASH:
                return g_knockbackConfig.grenadeLauncher;
        case MOD_ROCKET:
        case MOD_ROCKET_SPLASH:
                return selfInflicted ? g_knockbackConfig.rocketLauncherSelf : g_knockbackConfig.rocketLauncher;
        case MOD_PLASMA:
        case MOD_PLASMA_SPLASH:
                return selfInflicted ? g_knockbackConfig.plasmagunSelf : g_knockbackConfig.plasmagun;
        case MOD_LIGHTNING:
        case MOD_LIGHTNING_DISCHARGE:
                return g_knockbackConfig.lightningGun;
        case MOD_RAILGUN:
        case MOD_RAILGUN_HEADSHOT:
                return g_knockbackConfig.railgun;
        case MOD_BFG:
        case MOD_BFG_SPLASH:
                return g_knockbackConfig.bfg;
        case MOD_GRAPPLE:
                return g_knockbackConfig.grapplingHook;
        case MOD_NAIL:
                return g_knockbackConfig.nailgun;
        case MOD_CHAINGUN:
                return g_knockbackConfig.chaingun;
        case MOD_PROXIMITY_MINE:
                return g_knockbackConfig.proximityLauncher;
        default:
                break;
        }

        return 1.0f;
}

static float G_KnockbackVerticalBoost( qboolean selfInflicted ) {
        return selfInflicted ? g_knockbackConfig.verticalSelf : g_knockbackConfig.vertical;
}

static float G_ApplyKnockbackCripple( gentity_t *targ, float knockbackValue, int dflags, float *outPenalty ) {
        float penalty = 0.0f;

        if ( outPenalty ) {
                *outPenalty = 0.0f;
        }

        if ( g_knockbackConfig.cripple <= 0.0f || !targ || !targ->client ) {
                return knockbackValue;
        }

        if ( ( targ->flags & FL_NO_KNOCKBACK ) || ( dflags & DAMAGE_NO_KNOCKBACK ) ) {
                return knockbackValue;
        }

        if ( targ->health <= 0 ) {
                return knockbackValue;
        }

        qboolean crouched = ( targ->client->ps.pm_flags & PMF_DUCKED ) ? qtrue : qfalse;
        int maxHealth = targ->client->ps.stats[STAT_MAX_HEALTH];
        int currentHealth = targ->client->ps.stats[STAT_HEALTH];
        qboolean weakened = ( maxHealth > 0 && currentHealth > 0 && currentHealth < maxHealth ) ? qtrue : qfalse;

        if ( !crouched && !weakened ) {
                return knockbackValue;
        }

        {
                float scale = 1.0f;

                if ( crouched ) {
                        scale -= g_knockbackConfig.cripple;
                }

                if ( weakened ) {
                        float deficitFraction = (float)( maxHealth - currentHealth ) / (float)maxHealth;

                        scale -= g_knockbackConfig.cripple * deficitFraction;
                }

                if ( scale < 0.0f ) {
                        scale = 0.0f;
                }

                penalty = knockbackValue - ( knockbackValue * scale );
        }

        if ( penalty < 0.0f ) {
                penalty = 0.0f;
        } else if ( penalty > knockbackValue ) {
                penalty = knockbackValue;
        }

        if ( outPenalty ) {
                *outPenalty = penalty;
        }

        return knockbackValue - penalty;
}
/*
=============
G_ApplyVampiricReward

Applies vampiric healing to the attacker when enabled and announces the reward.
=============
*/
static void G_ApplyVampiricReward( gentity_t *targ, gentity_t *attacker, int healthDamage ) {
	float		vampiricScale;
	int		maxHealth;
	int		initialHealth;
	int		healAmount;

	if ( !attacker || !attacker->client ) {
		return;
	}

	if ( attacker == targ ) {
		return;
	}

	if ( healthDamage <= 0 ) {
		return;
	}

	vampiricScale = g_vampiricDamage.value;
	if ( vampiricScale <= 0.0f ) {
		return;
	}

	if ( targ && targ->client && OnSameTeam( targ, attacker ) ) {
		return;
	}

	maxHealth = attacker->client->ps.stats[STAT_MAX_HEALTH];
	if ( maxHealth <= 0 ) {
		maxHealth = 100;
	}

	initialHealth = attacker->health;
	if ( initialHealth >= maxHealth ) {
		return;
	}

	healAmount = (int)( ( (float)healthDamage * vampiricScale ) + 0.5f );
	if ( healAmount <= 0 ) {
		return;
	}

	if ( initialHealth + healAmount > maxHealth ) {
		healAmount = maxHealth - initialHealth;
	}

	if ( healAmount <= 0 ) {
		return;
	}

	attacker->health = initialHealth + healAmount;
	attacker->client->ps.stats[STAT_HEALTH] = attacker->health;

	trap_SendServerCommand( attacker->s.number, "cp \"Vampiric heal\"" );
}

void G_Damage( gentity_t *targ, gentity_t *inflictor, gentity_t *attacker,
                           vec3_t dir, vec3_t point, int damage, int dflags, int mod ) {
	gclient_t	*client;
	int			take;
	int			save;
	int			asave;
	float		knockbackValue;
	int			knockbackInt;
	int			max;
	qboolean		selfInflicted;
	vec3_t		bouncedir, impactpoint;
	float		knockbackScale = 1.0f;
	float		cripplePenalty = 0.0f;
	float		knockbackPreClamp = 0.0f;
	float		knockbackMax = 0.0f;
	float		verticalBoostApplied = 0.0f;
	float		powerupScale;

	powerupScale = 1.0f;
	if (!targ->takedamage) {
		return;
	}

	// the intermission has allready been qualified for, so don't
	// allow any extra scoring
	if ( level.intermissionQueued ) {
		return;
	}
	if ( targ->client && mod != MOD_JUICED) {
		if ( targ->client->invulnerabilityTime > level.time) {
			if ( dir && point ) {
				G_InvulnerabilityEffect( targ, dir, point, impactpoint, bouncedir );
			}
			return;
		}
	}
	if ( !inflictor ) {
		inflictor = &g_entities[ENTITYNUM_WORLD];
	}
	if ( !attacker ) {
		attacker = &g_entities[ENTITYNUM_WORLD];
	}

	selfInflicted = ( targ == attacker );

	// shootable doors / buttons don't actually have any health
	if ( targ->s.eType == ET_MOVER ) {
		if ( targ->use && targ->moverState == MOVER_POS1 ) {
			targ->use( targ, inflictor, attacker );
		}
		return;
	}
	if( g_gametype.integer == GT_OBELISK && CheckObeliskAttack( targ, attacker ) ) {
		return;
	}
	// reduce damage by the attacker's handicap value
	// unless they are rocket jumping
	if ( attacker->client && attacker != targ ) {
		max = attacker->client->ps.stats[STAT_MAX_HEALTH];
		if( bg_itemlist[attacker->client->ps.stats[STAT_PERSISTANT_POWERUP]].giTag == PW_GUARD ) {
			max /= 2;
		}
		damage = damage * max / 100;
	}

	if ( attacker->client ) {
		float	ratingScale;
		int		scaledDamage;

		ratingScale = attacker->client->damageModifier;
		if ( ratingScale > 0.0f && ratingScale != 1.0f ) {
			scaledDamage = ( int )( ( (float)damage * ratingScale ) + 0.5f );
			if ( scaledDamage < 1 && damage > 0 ) {
				scaledDamage = 1;
			}

			damage = scaledDamage;
		}
	}

	client = targ->client;

	if ( client ) {
		if ( client->noclip ) {
			return;
		}
		if ( G_FreezeGametypeEnabled() && client->freezeProtectedUntil > level.time ) {
			if ( attacker && attacker != targ && attacker->client ) {
				return;
			}
		}
	}

	damage = G_ClampModDamage( damage, mod, attacker );

	if ( ( mod == MOD_RAILGUN || mod == MOD_RAILGUN_HEADSHOT ) && G_IsRailgunHeadshot( targ, point ) ) {
		mod = MOD_RAILGUN_HEADSHOT;
		damage += g_weaponConfig.railgunHeadshotDamage;
	}

	powerupScale = G_CalcPowerupDamageScale( attacker );
	if ( powerupScale != 1.0f ) {
		damage = (int)( ( (float)damage * powerupScale ) + 0.5f );
	}

	if ( !dir ) {
		dflags |= DAMAGE_NO_KNOCKBACK;
	} else {
		VectorNormalize(dir);
	}

	knockbackScale = G_KnockbackScaleForMOD( mod, selfInflicted );
	knockbackValue = (float)damage;
	knockbackValue *= knockbackScale;
	knockbackValue = G_ApplyKnockbackCripple( targ, knockbackValue, dflags, &cripplePenalty );

	{
		float maxKnockback = g_knockbackConfig.maxKnockback;

		if ( maxKnockback <= 0.0f ) {
			maxKnockback = 200.0f;
		}

		knockbackPreClamp = knockbackValue;
		knockbackMax = maxKnockback;

		if ( knockbackValue > maxKnockback ) {
			knockbackValue = maxKnockback;
		}
	}

	if ( targ->flags & FL_NO_KNOCKBACK ) {
		knockbackValue = 0.0f;
	}
	if ( dflags & DAMAGE_NO_KNOCKBACK ) {
		knockbackValue = 0.0f;
	}

	if ( g_debugDamage.integer ) {
		G_Printf( "knockback summary: dmg=%d scale=%.2f cripple=%.2f preClamp=%.2f cap=%.2f final=%.2f vertical=%.2f self=%d mod=%d\n",
				damage, knockbackScale, cripplePenalty, knockbackPreClamp, knockbackMax, knockbackValue, verticalBoostApplied, selfInflicted, mod );
	}

	knockbackInt = (int)( knockbackValue + 0.5f );
	if ( knockbackInt <= 0 && knockbackValue > 0.0f ) {
		knockbackInt = 1;
	}

	// figure momentum add, even if the damage won't be taken
	if ( knockbackValue > 0.0f && targ->client ) {
		vec3_t	kvel;
		float	mass;

		mass = 200;

		VectorScale (dir, g_knockback.value * knockbackValue / mass, kvel);
		{
			float verticalBoost = G_KnockbackVerticalBoost( selfInflicted );

			if ( verticalBoost != 0.0f ) {
				kvel[2] += verticalBoost;
			}

			verticalBoostApplied = verticalBoost;
		}
		VectorAdd (targ->client->ps.velocity, kvel, targ->client->ps.velocity);

		// set the timer so that the other client can't cancel
		// out the movement immediately
		if ( !targ->client->ps.pm_time ) {
			int		t;

			t = (int)( knockbackValue * 2.0f );
			if ( g_knockbackConfig.cripple > 0.0f ) {
				int floorValue = (int)g_knockbackConfig.cripple;

				if ( floorValue > t ) {
					t = floorValue;
				}
			}
			if ( t > 200 ) {
				t = 200;
			}
			if ( t < 0 ) {
				t = 0;
			}
			targ->client->ps.pm_time = t;
			targ->client->ps.pm_flags |= PMF_TIME_KNOCKBACK;
		}
	}

	// check for completely getting out of the damage
	if ( !(dflags & DAMAGE_NO_PROTECTION) ) {

		// if TF_NO_FRIENDLY_FIRE is set, don't do damage to the target
		// if the attacker was on the same team
		if ( mod != MOD_JUICED && targ != attacker && !(dflags & DAMAGE_NO_TEAM_PROTECTION) && OnSameTeam (targ, attacker)  ) {
			if ( !g_friendlyFire.integer ) {
				return;
			}
		}
		if (mod == MOD_PROXIMITY_MINE) {
			if (inflictor && inflictor->parent && OnSameTeam(targ, inflictor->parent)) {
				return;
			}
			if (targ == attacker) {
				return;
			}
		}

		// check for godmode
		if ( targ->flags & FL_GODMODE ) {
			return;
		}
	}

	// battlesuit protects from all radius damage (but takes knockback)
	// and protects 50% against all damage
	if ( client && client->ps.powerups[PW_BATTLESUIT] ) {
		G_AddEvent( targ, EV_POWERUP_BATTLESUIT, 0 );
		if ( ( dflags & DAMAGE_RADIUS ) || ( mod == MOD_FALLING ) ) {
			return;
		}
		damage *= G_BattleSuitDamageScale();
	}

	// add to the attacker's hit counter (if the target isn't a general entity like a prox mine)
	if ( attacker->client && targ != attacker && targ->health > 0
			&& targ->s.eType != ET_MISSILE
			&& targ->s.eType != ET_GENERAL) {
		if ( OnSameTeam( targ, attacker ) ) {
			attacker->client->ps.persistant[PERS_HITS]--;
		} else {
			attacker->client->ps.persistant[PERS_HITS]++;
		}
		attacker->client->ps.persistant[PERS_ATTACKEE_ARMOR] = (targ->health<<8)|(client->ps.stats[STAT_ARMOR]);
	}

	// always give half damage if hurting self
	// calculated after knockback, so rocket jumping works
	if ( targ == attacker) {
		damage *= 0.5;
	}

	if ( damage < 1 ) {
		damage = 1;
	}
	take = damage;
	save = 0;

	// save some from armor
	asave = CheckArmor (targ, take, dflags);
	take -= asave;
	if ( take > 0 ) {
		G_RRHandleDamageScore( attacker, targ, take );
	}

	if ( attacker->client && client && attacker != targ && OnSameTeam( targ, attacker ) ) {
		int teamDamage = take + asave;

		if ( teamDamage > 0 ) {
			G_ComplaintConsiderForDamage( attacker, targ, teamDamage );
		}
	}

	if ( g_debugDamage.integer ) {
		G_Printf( "%i: client:%i health:%i damage:%i armor:%i\n", level.time, targ->s.number,
			targ->health, take, asave );
	}

	// add to the damage inflicted on a player this frame
	// the total will be turned into screen blends and view angle kicks
	// at the end of the frame
	if ( client ) {
		if ( attacker ) {
			client->ps.persistant[PERS_ATTACKER] = attacker->s.number;
		} else {
			client->ps.persistant[PERS_ATTACKER] = ENTITYNUM_WORLD;
		}
		client->damage_armor += asave;
		client->damage_blood += take;
		client->damage_knockback += knockbackInt;
		if ( dir ) {
			VectorCopy ( dir, client->damage_from );
			client->damage_fromWorld = qfalse;
		} else {
			VectorCopy ( targ->r.currentOrigin, client->damage_from );
			client->damage_fromWorld = qtrue;
		}
	}

	// See if it's the player hurting the emeny flag carrier
	if( g_gametype.integer == GT_CTF || g_gametype.integer == GT_1FCTF ) {
		Team_CheckHurtCarrier(targ, attacker);
	}

	if (targ->client) {
		// set the last client who damaged the target
		targ->client->lasthurt_client = attacker->s.number;
		targ->client->lasthurt_mod = mod;
	}

	// do the damage
	if ( take ) {
		targ->health = targ->health - take;
		if ( targ->client ) {
			targ->client->ps.stats[STAT_HEALTH] = targ->health;
		}

		G_ApplyVampiricReward( targ, attacker, take );

		if ( targ->health <= 0 ) {
			if ( client )
				targ->flags |= FL_NO_KNOCKBACK;

			if (targ->health < -999)
				targ->health = -999;

			targ->enemy = attacker;
			targ->die (targ, inflictor, attacker, take, mod);
			return;
		} else if ( targ->pain ) {
			targ->pain (targ, attacker, take);
		}
	}
}


/*
============
CanDamage

Returns qtrue if the inflictor can directly damage the target.  Used for
explosions and melee attacks.
============
*/
qboolean CanDamage (gentity_t *targ, vec3_t origin) {
	vec3_t	dest;
	trace_t	tr;
	vec3_t	midpoint;

	// use the midpoint of the bounds instead of the origin, because
	// bmodels may have their origin is 0,0,0
	VectorAdd (targ->r.absmin, targ->r.absmax, midpoint);
	VectorScale (midpoint, 0.5, midpoint);

	VectorCopy (midpoint, dest);
	trap_Trace ( &tr, origin, vec3_origin, vec3_origin, dest, ENTITYNUM_NONE, MASK_SOLID);
	if (tr.fraction == 1.0 || tr.entityNum == targ->s.number)
		return qtrue;

	// this should probably check in the plane of projection, 
	// rather than in world coordinate, and also include Z
	VectorCopy (midpoint, dest);
	dest[0] += 15.0;
	dest[1] += 15.0;
	trap_Trace ( &tr, origin, vec3_origin, vec3_origin, dest, ENTITYNUM_NONE, MASK_SOLID);
	if (tr.fraction == 1.0)
		return qtrue;

	VectorCopy (midpoint, dest);
	dest[0] += 15.0;
	dest[1] -= 15.0;
	trap_Trace ( &tr, origin, vec3_origin, vec3_origin, dest, ENTITYNUM_NONE, MASK_SOLID);
	if (tr.fraction == 1.0)
		return qtrue;

	VectorCopy (midpoint, dest);
	dest[0] -= 15.0;
	dest[1] += 15.0;
	trap_Trace ( &tr, origin, vec3_origin, vec3_origin, dest, ENTITYNUM_NONE, MASK_SOLID);
	if (tr.fraction == 1.0)
		return qtrue;

	VectorCopy (midpoint, dest);
	dest[0] -= 15.0;
	dest[1] -= 15.0;
	trap_Trace ( &tr, origin, vec3_origin, vec3_origin, dest, ENTITYNUM_NONE, MASK_SOLID);
	if (tr.fraction == 1.0)
		return qtrue;


	return qfalse;
}


/*
============
G_RadiusDamage
============
*/
qboolean G_RadiusDamage ( vec3_t origin, gentity_t *attacker, float damage, float radius,
					 gentity_t *ignore, int mod, qboolean *splashMidAir ) {
	float		points, dist;
	gentity_t	*ent;
	int			entityList[MAX_GENTITIES];
	int			numListedEntities;
	vec3_t		mins, maxs;
	vec3_t		v;
	vec3_t		dir;
	int			i, e;
	qboolean	hitClient = qfalse;
	qboolean	splashAwardMidAir;

	if ( radius < 1 ) {
		radius = 1;
	}

	splashAwardMidAir = qfalse;

	for ( i = 0 ; i < 3 ; i++ ) {
		mins[i] = origin[i] - radius;
		maxs[i] = origin[i] + radius;
	}

	numListedEntities = trap_EntitiesInBox( mins, maxs, entityList, MAX_GENTITIES );

	for ( e = 0 ; e < numListedEntities ; e++ ) {
		ent = &g_entities[entityList[ e ]];

		if (ent == ignore)
			continue;
		if (!ent->takedamage)
			continue;

		// find the distance from the edge of the bounding box
		for ( i = 0 ; i < 3 ; i++ ) {
			if ( origin[i] < ent->r.absmin[i] ) {
				v[i] = ent->r.absmin[i] - origin[i];
			} else if ( origin[i] > ent->r.absmax[i] ) {
				v[i] = origin[i] - ent->r.absmax[i];
			} else {
				v[i] = 0;
			}
		}

		dist = VectorLength( v );
		if ( dist >= radius ) {
			continue;
		}

		points = damage * ( 1.0 - dist / radius );

		if( CanDamage (ent, origin) ) {
			if( LogAccuracyHit( ent, attacker ) ) {
				hitClient = qtrue;
			}

			if ( !splashAwardMidAir
				&& ( mod == MOD_ROCKET_SPLASH || mod == MOD_PLASMA_SPLASH || mod == MOD_BFG_SPLASH )
				&& G_IsMidAirEligibleTarget( ent ) ) {
				splashAwardMidAir = qtrue;
			}
			VectorSubtract (ent->r.currentOrigin, origin, dir);
			// push the center of mass higher than the origin so players
			// get knocked into the air more
			dir[2] += 24;
			G_Damage (ent, NULL, attacker, dir, origin, (int)points, DAMAGE_RADIUS, mod);
		}
	}

	if ( splashMidAir ) {
		*splashMidAir = splashAwardMidAir;
	}

	return hitClient;
}

