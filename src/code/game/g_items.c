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
#include "g_local.h"
#include "g_rankings.h"
#include <limits.h>

/*

  Items are any object that a player can touch to gain some effect.

  Pickup will return the number of seconds until they should respawn.

  all items should pop when dropped in lava or slime

  Respawnable items don't actually go away when picked up, they are
  just made invisible and untouchable.  This allows them to ride
  movers and respawn apropriately.
*/


#define RESPAWN_ARMOR		25
#define RESPAWN_HEALTH		35
#define RESPAWN_AMMO		40
#define RESPAWN_HOLDABLE	60
#define RESPAWN_MEGAHEALTH	35//120
static const keyItemDef_t g_keyItemDefs[] = {
	{ KEY_FLAG_SILVER, "item_key_silver" },
	{ KEY_FLAG_GOLD, "item_key_gold" },
	{ KEY_FLAG_MASTER, "item_key_master" }
};

typedef struct weaponUnlockDef_s {
	weapon_t	weapon;
	int		threshold;
} weaponUnlockDef_t;

static const weaponUnlockDef_t s_weaponUnlockDefs[] = {
	{ WP_MACHINEGUN, 0 },
	{ WP_SHOTGUN, 1 },
	{ WP_GRENADE_LAUNCHER, 1 },
	{ WP_ROCKET_LAUNCHER, 2 },
	{ WP_LIGHTNING, 3 },
	{ WP_RAILGUN, 4 },
	{ WP_PLASMAGUN, 3 },
	{ WP_BFG, 5 },
	{ WP_GRAPPLING_HOOK, 0 },
	{ WP_NAILGUN, 2 },
	{ WP_PROX_LAUNCHER, 3 },
	{ WP_CHAINGUN, 4 },
	{ WP_HEAVY_MACHINEGUN, 2 },
	{ WP_NUM_WEAPONS, -1 }
};

/*
===============
G_GetClientUnlockProgress

Parses the player's unlock tier from their userinfo, defaulting to fully unlocked when absent.
===============
*/
static int G_GetClientUnlockProgress( const gclient_t *client ) {
	const char	*unlockValue;
	int		progress;

	if ( !client ) {
		return INT_MAX;
	}

	unlockValue = client->pers.userinfo[0] ? Info_ValueForKey( client->pers.userinfo, "unlock" ) : "";
	if ( !unlockValue || !unlockValue[0] ) {
		return INT_MAX;
	}

	progress = atoi( unlockValue );
	if ( progress < 0 ) {
		progress = 0;
	}

	return progress;
}

/*
===============
G_LookupWeaponUnlockThreshold

Returns the unlock threshold for the given weapon index.
===============
*/
static int G_LookupWeaponUnlockThreshold( weapon_t weapon ) {
	const weaponUnlockDef_t	*def;

	for ( def = s_weaponUnlockDefs ; def->weapon != WP_NUM_WEAPONS ; ++def ) {
		if ( def->weapon == weapon ) {
			return def->threshold;
		}
	}

	return 0;
}

/*
===============
G_WeaponUnlockedForClient

Returns qtrue when a player's unlock tier satisfies the weapon's unlock threshold.
===============
*/
static qboolean G_WeaponUnlockedForClient( gentity_t *ent, weapon_t weapon ) {
	int		progress;
	int		threshold;
	gitem_t	*item;

	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return qtrue;
	}

	if ( level.trainingMapActive ) {
		return qtrue;
	}

	threshold = G_LookupWeaponUnlockThreshold( weapon );
	if ( threshold <= 0 ) {
		return qtrue;
	}

	progress = G_GetClientUnlockProgress( ent ? ent->client : NULL );
	if ( progress >= threshold ) {
		return qtrue;
	}

	if ( ent && ent->client ) {
		item = BG_FindItemForWeapon( weapon );
		trap_SendServerCommand( ent - g_entities, va( "cp \"%s locked (tier %i)\"", item ? item->pickup_name : "Weapon", threshold ) );
	}

	return qfalse;
}


/*
===============
G_KeyItemDefs

Returns the static key definition table so callers can iterate over supported key items.
===============
*/
const keyItemDef_t *G_KeyItemDefs( int *count ) {
	if ( count ) {
		*count = sizeof( g_keyItemDefs ) / sizeof( g_keyItemDefs[0] );
	}

	return g_keyItemDefs;
}

/*
===============
G_KeyItemForBit

Resolves the gitem definition for a particular key mask bit.
===============
*/
gitem_t *G_KeyItemForBit( int bit ) {
	int			 i;
	int			 count;
	const keyItemDef_t	*defs;

	defs = G_KeyItemDefs( &count );
	for ( i = 0 ; i < count ; i++ ) {
		if ( defs[i].bit != bit ) {
			continue;
		}

		return BG_FindItemByClassname( defs[i].classname );
	}

	return NULL;
}

#define	RESPAWN_POWERUP		120

/*
=============
G_MatchFactoryDropAllowed

Returns whether the active match factory configuration permits item drops.
=============
*/
static qboolean G_MatchFactoryDropAllowed( void ) {
	return level.matchAllowItemDrops ? qtrue : qfalse;
}

/*
=============
G_MatchFactoryBounceAllowed

Returns whether dropped and spawned items should bounce.
=============
*/
static qboolean G_MatchFactoryBounceAllowed( void ) {
	return level.matchAllowItemBounce ? qtrue : qfalse;
}

/*
=============
G_BuildItemTossVelocity

Constructs the base toss velocity for dropped and launched items.
=============
*/
static void G_BuildItemTossVelocity( gentity_t *ent, gitem_t *item, float angle, vec3_t velocity ) {
	vec3_t	angles;
	vec3_t	forward;

	if ( !ent || !item ) {
		VectorClear( velocity );
		return;
	}

	VectorCopy( ent->s.apos.trBase, angles );
	angles[YAW] += angle;
	angles[PITCH] = 0;

	AngleVectors( angles, forward, NULL, NULL );

	if ( item->giType == IT_TEAM && g_flagConfig.flagPhysics ) {
		VectorScale( forward, g_flagConfig.throwFlagVelocity, velocity );
		if ( ent->client ) {
			vec3_t	playerVelocity;

			VectorScale( ent->client->ps.velocity, g_flagConfig.throwFlagForwardMult, playerVelocity );
			VectorAdd( velocity, playerVelocity, velocity );
		}
	} else {
		VectorScale( forward, 150, velocity );
	}

	velocity[2] += 200 + crandom() * 50;
}

/*
===============
G_ApplyItemBounceSettings

Configures physics bounce behaviour for dropped items.
===============
*/

/*
=============
G_GetFlightRefuelMilliseconds

Scales the amount of time granted when refuelling the Flight powerup.
=============
*/
static int G_GetFlightRefuelMilliseconds( int baseMilliseconds ) {
	float	refuelRate;
	float	scaled;
	float	maxMilliseconds;

	if ( baseMilliseconds <= 0 ) {
		return 0;
	}

	refuelRate = g_flightRefuelRate.value;
	if ( refuelRate <= 0.0f ) {
		return baseMilliseconds;
	}

	scaled = (float)baseMilliseconds * refuelRate;
	maxMilliseconds = (float)INT_MAX;
	if ( scaled < 1.0f ) {
		scaled = 1.0f;
	} else if ( scaled > maxMilliseconds ) {
		scaled = maxMilliseconds;
	}

	return (int)scaled;
}

/*
=============
G_ShouldUseDroppedHealthCount

Returns qtrue when a dropped health pickup should use its stored count.
=============
*/
static qboolean G_ShouldUseDroppedHealthCount( const gentity_t *ent ) {
	if ( !ent || ent->count <= 0 ) {
		return qfalse;
	}

	if ( !( ent->flags & FL_DROPPED_ITEM ) ) {
		return qtrue;
	}

	return g_dropDamagedHealth.integer ? qtrue : qfalse;
}

static void G_ApplyItemBounceSettings( gentity_t *dropped, gitem_t *item ) {
	qboolean	factoryAllowsBounce;

	if ( !dropped ) {
		return;
	}

	factoryAllowsBounce = G_MatchFactoryBounceAllowed();

	if ( !item || item->giType != IT_TEAM || !g_flagConfig.flagPhysics ) {
		if ( factoryAllowsBounce ) {
			dropped->s.eFlags |= EF_BOUNCE_HALF;
			dropped->physicsBounce = 0.50f;
		} else {
			dropped->s.eFlags &= ~EF_BOUNCE_HALF;
			dropped->physicsBounce = 0.0f;
		}
		return;
	}

	if ( factoryAllowsBounce && g_flagConfig.flagPhysics ) {
		dropped->s.eFlags |= EF_BOUNCE_HALF;
		dropped->physicsBounce = g_flagConfig.flagBounce;
	} else {
		dropped->s.eFlags &= ~EF_BOUNCE_HALF;
		dropped->physicsBounce = 0.0f;
	}
}


//======================================================================

int Pickup_Powerup( gentity_t *ent, gentity_t *other ) {
	int			quantity;
	int			i;
	gclient_t	*client;

	if ( !other->client->ps.powerups[ent->item->giTag] ) {
		// round timing to seconds to make multiple powerup timers
		// count in sync
		other->client->ps.powerups[ent->item->giTag] = 
			level.time - ( level.time % 1000 );
	}

	if ( ent->count ) {
		quantity = ent->count;
	} else {
		quantity = ent->item->quantity;
	}

	if ( ent->item->giTag == PW_FLIGHT ) {
		int	milliseconds;

		milliseconds = G_GetFlightRefuelMilliseconds( quantity * 1000 );
		other->client->ps.powerups[ent->item->giTag] += milliseconds;
	} else {
		other->client->ps.powerups[ent->item->giTag] += quantity * 1000;
	}

	if ( ent->item->giTag == PW_QUAD ) {
		G_QuadHogOnPickup( other );
	}

	// give any nearby players a "denied" anti-reward
	for ( i = 0 ; i < level.maxclients ; i++ ) {
		vec3_t		delta;
		float		len;
		vec3_t		forward;
		trace_t		tr;

		client = &level.clients[i];
		if ( client == other->client ) {
			continue;
		}
		if ( client->pers.connected == CON_DISCONNECTED ) {
			continue;
		}
		if ( client->ps.stats[STAT_HEALTH] <= 0 ) {
			continue;
		}

    // if same team in team game, no sound
    // cannot use OnSameTeam as it expects to g_entities, not clients
  	if ( g_gametype.integer >= GT_TEAM && other->client->sess.sessionTeam == client->sess.sessionTeam  ) {
      continue;
    }

		// if too far away, no sound
		VectorSubtract( ent->s.pos.trBase, client->ps.origin, delta );
		len = VectorNormalize( delta );
		if ( len > 192 ) {
			continue;
		}

		// if not facing, no sound
		AngleVectors( client->ps.viewangles, forward, NULL, NULL );
		if ( DotProduct( delta, forward ) < 0.4 ) {
			continue;
		}

		// if not line of sight, no sound
		trap_Trace( &tr, client->ps.origin, NULL, NULL, ent->s.pos.trBase, ENTITYNUM_NONE, CONTENTS_SOLID );
		if ( tr.fraction != 1.0 ) {
			continue;
		}

		// anti-reward
		client->ps.persistant[PERS_PLAYEREVENTS] ^= PLAYEREVENT_DENIEDREWARD;
	}
	return RESPAWN_POWERUP;
}

//======================================================================

int Pickup_PersistantPowerup( gentity_t *ent, gentity_t *other ) {
	int		clientNum;
	char	userinfo[MAX_INFO_STRING];
	float	handicap;
	int		max;

	other->client->ps.stats[STAT_PERSISTANT_POWERUP] = ent->item - bg_itemlist;
	other->client->persistantPowerup = ent;

	switch( ent->item->giTag ) {
	case PW_GUARD:
		clientNum = other->client->ps.clientNum;
		trap_GetUserinfo( clientNum, userinfo, sizeof(userinfo) );
		handicap = atof( Info_ValueForKey( userinfo, "handicap" ) );
		if( handicap<=0.0f || handicap>100.0f) {
			handicap = 100.0f;
		}
		max = (int)(2 *  handicap);

		other->health = max;
		other->client->ps.stats[STAT_HEALTH] = max;
		other->client->ps.stats[STAT_MAX_HEALTH] = max;
		other->client->ps.stats[STAT_ARMOR] = max;
		other->client->pers.maxHealth = max;

		break;

	case PW_SCOUT:
		clientNum = other->client->ps.clientNum;
		trap_GetUserinfo( clientNum, userinfo, sizeof(userinfo) );
		handicap = atof( Info_ValueForKey( userinfo, "handicap" ) );
		if( handicap<=0.0f || handicap>100.0f) {
			handicap = 100.0f;
		}
		other->client->pers.maxHealth = handicap;
		other->client->ps.stats[STAT_ARMOR] = 0;
		break;

	case PW_DOUBLER:
		clientNum = other->client->ps.clientNum;
		trap_GetUserinfo( clientNum, userinfo, sizeof(userinfo) );
		handicap = atof( Info_ValueForKey( userinfo, "handicap" ) );
		if( handicap<=0.0f || handicap>100.0f) {
			handicap = 100.0f;
		}
		other->client->pers.maxHealth = handicap;
		break;
	case PW_AMMOREGEN:
		clientNum = other->client->ps.clientNum;
		trap_GetUserinfo( clientNum, userinfo, sizeof(userinfo) );
		handicap = atof( Info_ValueForKey( userinfo, "handicap" ) );
		if( handicap<=0.0f || handicap>100.0f) {
			handicap = 100.0f;
		}
		other->client->pers.maxHealth = handicap;
		memset(other->client->ammoTimes, 0, sizeof(other->client->ammoTimes));
		break;
	default:
		clientNum = other->client->ps.clientNum;
		trap_GetUserinfo( clientNum, userinfo, sizeof(userinfo) );
		handicap = atof( Info_ValueForKey( userinfo, "handicap" ) );
		if( handicap<=0.0f || handicap>100.0f) {
			handicap = 100.0f;
		}
		other->client->pers.maxHealth = handicap;
		break;
	}

	return -1;
}

//======================================================================

int Pickup_Holdable( gentity_t *ent, gentity_t *other ) {

        other->client->ps.stats[STAT_HOLDABLE_ITEM] = ent->item - bg_itemlist;

        if( ent->item->giTag == HI_KAMIKAZE ) {
                other->client->ps.eFlags |= EF_KAMIKAZE;
        }

        return RESPAWN_HOLDABLE;
}

/*
===============
Pickup_Key

Awards the configured key bit to the activator and prevents the source entity from respawning automatically.
===============
*/
static int Pickup_Key( gentity_t *ent, gentity_t *other ) {
	int	keyBit;

	if ( !ent || !ent->item || !other ) {
		return 0;
	}

	keyBit = ent->item->giTag;
	if ( keyBit <= 0 ) {
		return 0;
	}

	other->keyMask |= keyBit;

	if ( other->client ) {
		trap_RankReportInt( other->s.number, -1, QGR_KEY_FLAG_PICKUP, 1, 1 );
	}

	return -1;
}


//======================================================================

/*
=============
G_FactoryAmmoPacksEnabled

Returns whether the server factory configuration has ammo pack overrides enabled.
=============
*/
static qboolean G_FactoryAmmoPacksEnabled( void ) {
	return ( g_factoryCvarConfig.ammoPackEnabled || g_factoryCvarConfig.ammoPackHackEnabled ) ? qtrue : qfalse;
}

/*
=============
G_GetConfiguredAmmoRespawnSeconds

Resolves the respawn time used for ammo pickups when factory settings are active.
=============
*/
static int G_GetConfiguredAmmoRespawnSeconds( void ) {
	int		respawn = g_factoryCvarConfig.ammoRespawnSeconds;

	if ( respawn <= 0 ) {
		respawn = RESPAWN_AMMO;
	}

	return respawn;
}

/*
=============
G_ApplyPowerupRespawnOverride

Overrides the respawn time for powerups when factories supply a non-zero delay.
=============
*/
static int G_ApplyPowerupRespawnOverride( const gentity_t *ent, int respawnSeconds ) {
	int		factorySeconds;

	if ( respawnSeconds <= 0 || !ent || !ent->item ) {
		return respawnSeconds;
	}

	if ( ent->item->giType != IT_POWERUP ) {
		return respawnSeconds;
	}

	factorySeconds = g_factoryCvarConfig.powerupRespawnSeconds;
	if ( factorySeconds <= 0 ) {
		return respawnSeconds;
	}

	return factorySeconds;
}

/*
=============
G_GetAmmoPackPickupCount

Returns the ammo amount granted by a pickup for the supplied weapon, applying
factory overrides when available.
=============
*/
static int G_GetAmmoPackPickupCount( weapon_t weapon, int fallback ) {
	int	basePickup;
	int	configured;

	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return fallback;
	}

	basePickup = fallback > 0 ? fallback : BG_GetWeaponAmmoPackSize( weapon );
	if ( !G_FactoryAmmoPacksEnabled() ) {
		return basePickup;
	}

	configured = g_ammoPackConfig.weaponPickup[weapon];
	if ( configured > 0 ) {
		return configured;
	}

	return basePickup;
}

/*
=============
G_GetAmmoPackMaxStack

Returns the maximum stack size that ammo packs should clamp to for a weapon.
=============
*/
static int G_GetAmmoPackMaxStack( weapon_t weapon, int fallbackPack ) {
	int	baseStack;
	int	configured;

	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return 0;
	}

	if ( fallbackPack <= 0 ) {
		fallbackPack = BG_GetWeaponAmmoPackSize( weapon );
	}

	baseStack = BG_GetWeaponAmmoPackMaxStack( weapon );
	if ( baseStack <= 0 ) {
		baseStack = fallbackPack;
	}

	if ( !G_FactoryAmmoPacksEnabled() ) {
		return baseStack;
	}

	configured = g_ammoPackConfig.weaponMax[weapon];
	if ( configured > 0 ) {
		return configured;
	}

	return baseStack;
}

/*
=============
G_ResolveAmmoPickupAmount

Determines how much ammo an entity should grant, taking server overrides into
account.
=============
*/
static int G_ResolveAmmoPickupAmount( const gentity_t *ent ) {
	int	fallback;

	if ( !ent || !ent->item ) {
		return 0;
	}

	if ( ent->count < 0 ) {
		return 0;
	}

	if ( ent->count > 0 ) {
		return ent->count;
	}

	fallback = ent->item->quantity;
	if ( fallback <= 0 ) {
		fallback = BG_GetWeaponAmmoPackSize( ent->item->giTag );
	}

	return G_GetAmmoPackPickupCount( ent->item->giTag, fallback );
}

/*
=============
Add_Ammo

Adds ammo to the supplied client while clamping to the configured maximum.
=============
*/
void Add_Ammo (gentity_t *ent, int weapon, int count)
{
	weapon_t weaponIndex;
	int maxStack;
	int defaultPack;

	if ( !ent || !ent->client ) {
		return;
	}

	weaponIndex = (weapon_t)weapon;
	if ( weaponIndex <= WP_NONE || weaponIndex >= WP_NUM_WEAPONS ) {
		return;
	}

	ent->client->ps.ammo[weapon] += count;

	if ( ent->client->ps.ammo[weapon] < 0 ) {
		ent->client->ps.ammo[weapon] = 0;
	}

	defaultPack = BG_GetWeaponAmmoPackSize( weaponIndex );
	maxStack = G_GetAmmoPackMaxStack( weaponIndex, defaultPack );

	if ( maxStack > 0 && ent->client->ps.ammo[weapon] > maxStack ) {
		ent->client->ps.ammo[weapon] = maxStack;
	}
}

/*
=============
Pickup_Ammo

Processes an ammo pickup for the specified entity and client.
=============
*/
int Pickup_Ammo (gentity_t *ent, gentity_t *other)
{
	int			quantity;
	int			respawn;

	quantity = G_ResolveAmmoPickupAmount( ent );

	if ( quantity < 0 ) {
		quantity = 0;
	}

	Add_Ammo (other, ent->item->giTag, quantity);

	respawn = G_GetConfiguredAmmoRespawnSeconds();
	if ( respawn <= 0 ) {
		respawn = RESPAWN_AMMO;
	}

	if ( level.suddenDeathActive && !g_factoryCvarConfig.suddenDeathRespawn ) {
		return 0;
	}

	return respawn;
}

//======================================================================


/*
=============
Pickup_Weapon

Handles weapon pickups and issues any ammo associated with the weapon.
=============
*/
int Pickup_Weapon (gentity_t *ent, gentity_t *other) {
	int		quantity;
	weapon_t	weapon;
	int		basePickup;

	weapon = ent->item ? (weapon_t)ent->item->giTag : WP_NONE;
	basePickup = G_GetAmmoPackPickupCount( weapon, ent->item ? ent->item->quantity : 0 );

	if ( !G_WeaponUnlockedForClient( other, weapon ) ) {
		return 0;
	}

	if ( ent->count < 0 ) {
		quantity = 0; // None for you, sir!
	} else if ( ent->count > 0 ) {
		quantity = ent->count;
	} else {
		quantity = basePickup;

		if ( quantity <= 0 ) {
			quantity = ent->item ? ent->item->quantity : 0;
		}

		if ( !( ent->flags & FL_DROPPED_ITEM ) && g_gametype.integer != GT_TEAM ) {
			if ( weapon > WP_NONE && weapon < WP_NUM_WEAPONS && basePickup > 0
				&& other->client->ps.ammo[weapon] < basePickup ) {
				quantity = basePickup - other->client->ps.ammo[weapon];
			} else {
				quantity = 1;		// only add a single shot
			}
		}
	}

	if ( quantity < 0 ) {
		quantity = 0;
	}

	// add the weapon
	other->client->ps.stats[STAT_WEAPONS] |= ( 1 << ent->item->giTag );

	Add_Ammo( other, ent->item->giTag, quantity );

	if ( ent->item->giTag == WP_GRAPPLING_HOOK ) {
		other->client->ps.ammo[ent->item->giTag] = -1; // unlimited ammo
	}

	// team deathmatch has slow weapon respawns
	if ( g_gametype.integer == GT_TEAM ) {
		return g_weaponTeamRespawn.integer;
	}

	return g_weaponRespawn.integer;
}


//======================================================================

/*
=============
Pickup_Health

Applies health pickups while respecting the configured overstack bounds.
=============
*/
int Pickup_Health (gentity_t *ent, gentity_t *other) {
	int			max;
	int			quantity;
	playerState_t	*ps;

	if ( !other || !other->client ) {
		return RESPAWN_HEALTH;
	}

	ps = &other->client->ps;
	max = BG_GetHealthUpperBound( ps, ent->item ? ent->item->quantity : 0 );
	if ( max <= 0 ) {
		max = other->client->ps.stats[STAT_MAX_HEALTH];
	}

	if ( G_ShouldUseDroppedHealthCount( ent ) ) {
		quantity = ent->count;
	} else if ( ent->item ) {
		quantity = ent->item->quantity;
	} else {
		quantity = 0;
	}

	other->health += quantity;

	if ( other->health > max ) {
		other->health = max;
	}
	ps->stats[STAT_HEALTH] = other->health;

	if ( ent->item->quantity == 100 ) {		// mega health respawns slow
		return RESPAWN_MEGAHEALTH;
	}

	return RESPAWN_HEALTH;
}

//======================================================================

/*
=============
Pickup_Armor

Adds armor from pickups and clamps it based on the player's current powerups.
=============
*/
int Pickup_Armor( gentity_t *ent, gentity_t *other ) {
	int		upperBound;
	playerState_t	*ps;

	if ( !other || !other->client ) {
		return RESPAWN_ARMOR;
	}

	ps = &other->client->ps;
	ps->stats[STAT_ARMOR] += ent->item->quantity;

	upperBound = BG_GetArmorUpperBound( ps );
	if ( upperBound > 0 && ps->stats[STAT_ARMOR] > upperBound ) {
		ps->stats[STAT_ARMOR] = upperBound;
	}

	return RESPAWN_ARMOR;
}

//======================================================================

/*
===============
RespawnItem
===============
*/
void RespawnItem( gentity_t *ent ) {
	// randomly select from teamed entities
	if (ent->team) {
		gentity_t	*master;
		int	count;
		int choice;

		if ( !ent->teammaster ) {
			G_Error( "RespawnItem: bad teammaster");
		}
		master = ent->teammaster;

		for (count = 0, ent = master; ent; ent = ent->teamchain, count++)
			;

		choice = rand() % count;

		for (count = 0, ent = master; count < choice; ent = ent->teamchain, count++)
			;
	}

	ent->r.contents = CONTENTS_TRIGGER;
	ent->s.eFlags &= ~EF_NODRAW;
	ent->r.svFlags &= ~SVF_NOCLIENT;
	trap_LinkEntity (ent);

	if ( ent->item->giType == IT_POWERUP ) {
		// play powerup spawn sound to all clients
		gentity_t	*te;

		// if the powerup respawn sound should Not be global
		if (ent->speed) {
			te = G_TempEntity( ent->s.pos.trBase, EV_GENERAL_SOUND );
		}
		else {
			te = G_TempEntity( ent->s.pos.trBase, EV_GLOBAL_SOUND );
		}
		te->s.eventParm = G_SoundIndex( "sound/items/poweruprespawn.wav" );
		te->r.svFlags |= SVF_BROADCAST;
	}

	if ( ent->item->giType == IT_HOLDABLE && ent->item->giTag == HI_KAMIKAZE ) {
		// play powerup spawn sound to all clients
		gentity_t	*te;

		// if the powerup respawn sound should Not be global
		if (ent->speed) {
			te = G_TempEntity( ent->s.pos.trBase, EV_GENERAL_SOUND );
		}
		else {
			te = G_TempEntity( ent->s.pos.trBase, EV_GLOBAL_SOUND );
		}
		te->s.eventParm = G_SoundIndex( "sound/items/kamikazerespawn.wav" );
		te->r.svFlags |= SVF_BROADCAST;
	}

	// play the normal respawn sound only to nearby clients
	G_AddEvent( ent, EV_ITEM_RESPAWN, 0 );

	ent->nextthink = 0;
}


/*
===============
Touch_Item
===============
*/
void Touch_Item (gentity_t *ent, gentity_t *other, trace_t *trace) {
	int			respawn;
	qboolean	predict;

	if (!other->client)
		return;
	if (other->health < 1)
		return;		// dead people can't pickup

	// the same pickup rules are used for client side and server side
	if ( !BG_CanItemBeGrabbed( g_gametype.integer, level.time, &ent->s, &other->client->ps ) ) {
		return;
	}

	G_LogPrintf( "Item: %i %s\n", other->s.number, ent->item->classname );

	predict = other->client->pers.predictItemPickup;

	// call the item-specific pickup function
	switch( ent->item->giType ) {
	case IT_WEAPON:
		respawn = Pickup_Weapon(ent, other);
//		predict = qfalse;
		break;
	case IT_AMMO:
		respawn = Pickup_Ammo(ent, other);
//		predict = qfalse;
		break;
	case IT_ARMOR:
		respawn = Pickup_Armor(ent, other);
		break;
	case IT_HEALTH:
		respawn = Pickup_Health(ent, other);
		break;
	case IT_POWERUP:
		respawn = Pickup_Powerup(ent, other);
		predict = qfalse;
		break;
	case IT_PERSISTANT_POWERUP:
		respawn = Pickup_PersistantPowerup(ent, other);
		break;
	case IT_TEAM:
		respawn = Pickup_Team(ent, other);
		break;
	case IT_HOLDABLE:
		respawn = Pickup_Holdable(ent, other);
		break;
	case IT_KEY:
		respawn = Pickup_Key( ent, other );
		break;
	default:
		return;
	}

	if ( !respawn ) {
		return;
	}

	// play the normal pickup sound
	if (predict) {
		G_AddPredictableEvent( other, EV_ITEM_PICKUP, ent->s.modelindex );
	} else {
		G_AddEvent( other, EV_ITEM_PICKUP, ent->s.modelindex );
	}

	// powerup pickups are global broadcasts
	if ( ent->item->giType == IT_POWERUP || ent->item->giType == IT_TEAM) {
		// if we want the global sound to play
		if (!ent->speed) {
			gentity_t	*te;

			te = G_TempEntity( ent->s.pos.trBase, EV_GLOBAL_ITEM_PICKUP );
			te->s.eventParm = ent->s.modelindex;
			te->r.svFlags |= SVF_BROADCAST;
		} else {
			gentity_t	*te;

			te = G_TempEntity( ent->s.pos.trBase, EV_GLOBAL_ITEM_PICKUP );
			te->s.eventParm = ent->s.modelindex;
			// only send this temp entity to a single client
			te->r.svFlags |= SVF_SINGLECLIENT;
			te->r.singleClient = other->s.number;
		}
	}

	// fire item targets
	G_UseTargets (ent, other);

	// wait of -1 will not respawn
	if ( ent->wait == -1 ) {
		ent->r.svFlags |= SVF_NOCLIENT;
		ent->s.eFlags |= EF_NODRAW;
		ent->r.contents = 0;
		ent->unlinkAfterEvent = qtrue;
		return;
	}

	// non zero wait overrides respawn time
	if ( ent->wait ) {
		respawn = ent->wait;
	}

	// random can be used to vary the respawn time
	if ( ent->random ) {
		respawn += crandom() * ent->random;
		if ( respawn < 1 ) {
			respawn = 1;
		}
	}

	respawn = G_ApplyPowerupRespawnOverride( ent, respawn );

	// dropped items will not respawn
	if ( ent->flags & FL_DROPPED_ITEM ) {
		ent->freeAfterEvent = qtrue;
	}

	// picked up items still stay around, they just don't
	// draw anything.  This allows respawnable items
	// to be placed on movers.
	ent->r.svFlags |= SVF_NOCLIENT;
	ent->s.eFlags |= EF_NODRAW;
	ent->r.contents = 0;

	// ZOID
	// A negative respawn times means to never respawn this item (but don't 
	// delete it).  This is used by items that are respawned by third party 
	// events such as ctf flags
	if ( respawn <= 0 ) {
		ent->nextthink = 0;
		ent->think = 0;
	} else {
		ent->nextthink = level.time + respawn * 1000;
		ent->think = RespawnItem;
	}
	trap_LinkEntity( ent );
}


//======================================================================

/*
================
LaunchItem

Spawns an item and tosses it forward
================
*/
gentity_t *LaunchItem( gitem_t *item, vec3_t origin, vec3_t velocity ) {
	gentity_t	*dropped;

	if ( !G_MatchFactoryDropAllowed() && item && item->giType != IT_TEAM && item->giType != IT_KEY ) {
		return NULL;
	}

	dropped = G_Spawn();

	dropped->s.eType = ET_ITEM;
	dropped->s.modelindex = item - bg_itemlist;	// store item number in modelindex
	dropped->s.modelindex2 = 1; // This is non-zero is it's a dropped item

	dropped->classname = item->classname;
	dropped->item = item;
	VectorSet (dropped->r.mins, -ITEM_RADIUS, -ITEM_RADIUS, -ITEM_RADIUS);
	VectorSet (dropped->r.maxs, ITEM_RADIUS, ITEM_RADIUS, ITEM_RADIUS);
	dropped->r.contents = CONTENTS_TRIGGER;

	dropped->touch = Touch_Item;

	G_SetOrigin( dropped, origin );
	dropped->s.pos.trType = TR_GRAVITY;
	dropped->s.pos.trTime = level.time;
	VectorCopy( velocity, dropped->s.pos.trDelta );

	G_ApplyItemBounceSettings( dropped, item );
	if ( ( g_gametype.integer == GT_CTF || g_gametype.integer == GT_1FCTF )			&& item->giType == IT_TEAM ) { // Special case for CTF flags
		int		dropTimeout;

		dropped->think = Team_DroppedFlagThink;
		dropTimeout = g_flagConfig.dropTimeoutMs;
		if ( dropTimeout <= 0 ) {
			dropped->timestamp = level.time;
			dropped->nextthink = level.time;
		} else {
			dropped->timestamp = level.time + dropTimeout;
			dropped->nextthink = dropped->timestamp;
		}
	} else { // auto-remove after 30 seconds
		dropped->think = G_FreeEntity;
		dropped->nextthink = level.time + 30000;
	}

	dropped->flags = FL_DROPPED_ITEM;

	trap_LinkEntity (dropped);

	return dropped;
}

/*
================
Drop_Item

Spawns an item and tosses it forward
================
*/
gentity_t *Drop_Item( gentity_t *ent, gitem_t *item, float angle ) {
	vec3_t	velocity;
	gentity_t	*dropped;

	if ( !item ) {
		return NULL;
	}

	if ( !G_MatchFactoryDropAllowed() && item->giType != IT_TEAM && item->giType != IT_KEY ) {
		return NULL;
	}

	G_BuildItemTossVelocity( ent, item, angle, velocity );

	dropped = LaunchItem( item, ent->s.pos.trBase, velocity );
	if ( dropped && ent && item->giType == IT_KEY ) {
		ent->keyMask &= ~item->giTag;
	}

	return dropped;
}

/*
=============
G_DropClientKeys

Drops all carried keys for the specified entity.
=============
*/
void G_DropClientKeys( gentity_t *ent ) {
	int				count;
	int				i;
	const keyItemDef_t	*defs;

	if ( !ent || !ent->keyMask ) {
		return;
	}

	defs = G_KeyItemDefs( &count );
	for ( i = 0 ; i < count ; i++ ) {
		const keyItemDef_t	*def;
		gitem_t			*item;

		def = &defs[i];
		if ( !( ent->keyMask & def->bit ) ) {
			continue;
		}

		item = BG_FindItemByClassname( def->classname );
		if ( !item ) {
			G_Printf( "WARNING: missing key definition for %s\n", def->classname );
			continue;
		}

		Drop_Item( ent, item, 0 );
	}

	ent->keyMask = 0;
}


/*
================
Use_Item

Respawn the item
================
*/
void Use_Item( gentity_t *ent, gentity_t *other, gentity_t *activator ) {
	RespawnItem( ent );
}

//======================================================================

/*
================
FinishSpawningItem

Traces down to find where an item should rest, instead of letting them
free fall from their spawn points
================
*/
void FinishSpawningItem( gentity_t *ent ) {
	trace_t		tr;
	vec3_t		dest;

	VectorSet( ent->r.mins, -ITEM_RADIUS, -ITEM_RADIUS, -ITEM_RADIUS );
	VectorSet( ent->r.maxs, ITEM_RADIUS, ITEM_RADIUS, ITEM_RADIUS );

	ent->s.eType = ET_ITEM;
	ent->s.modelindex = ent->item - bg_itemlist;		// store item number in modelindex
	ent->s.modelindex2 = 0; // zero indicates this isn't a dropped item

	ent->r.contents = CONTENTS_TRIGGER;
	ent->touch = Touch_Item;
	// useing an item causes it to respawn
	ent->use = Use_Item;

	if ( ent->spawnflags & 1 ) {
		// suspended
		G_SetOrigin( ent, ent->s.origin );
	} else {
		// drop to floor
		VectorSet( dest, ent->s.origin[0], ent->s.origin[1], ent->s.origin[2] - 4096 );
		trap_Trace( &tr, ent->s.origin, ent->r.mins, ent->r.maxs, dest, ent->s.number, MASK_SOLID );
		if ( tr.startsolid ) {
			G_Printf ("FinishSpawningItem: %s startsolid at %s\n", ent->classname, vtos(ent->s.origin));
			G_FreeEntity( ent );
			return;
		}

		// allow to ride movers
		ent->s.groundEntityNum = tr.entityNum;

		G_SetOrigin( ent, tr.endpos );
	}

	// team slaves and targeted items aren't present at start
	if ( ( ent->flags & FL_TEAMSLAVE ) || ent->targetname ) {
		ent->s.eFlags |= EF_NODRAW;
		ent->r.contents = 0;
		return;
	}

	// powerups don't spawn in for a while
	if ( ent->item->giType == IT_POWERUP ) {
		float	respawn;

		respawn = 45 + crandom() * 15;
		ent->s.eFlags |= EF_NODRAW;
		ent->r.contents = 0;
		ent->nextthink = level.time + respawn * 1000;
		ent->think = RespawnItem;
		return;
	}


	trap_LinkEntity (ent);
}


qboolean	itemRegistered[MAX_ITEMS];

/*
==================
G_CheckTeamItems
==================
*/
void G_CheckTeamItems( void ) {

	// Set up team stuff
	Team_InitGame();

	if( g_gametype.integer == GT_CTF ) {
		gitem_t	*item;

		// check for the two flags
		item = BG_FindItem( "Red Flag" );
		if ( !item || !itemRegistered[ item - bg_itemlist ] ) {
			G_Printf( S_COLOR_YELLOW "WARNING: No team_CTF_redflag in map" );
		}
		item = BG_FindItem( "Blue Flag" );
		if ( !item || !itemRegistered[ item - bg_itemlist ] ) {
			G_Printf( S_COLOR_YELLOW "WARNING: No team_CTF_blueflag in map" );
		}
	}
	if( g_gametype.integer == GT_1FCTF ) {
		gitem_t	*item;

		// check for all three flags
		item = BG_FindItem( "Red Flag" );
		if ( !item || !itemRegistered[ item - bg_itemlist ] ) {
			G_Printf( S_COLOR_YELLOW "WARNING: No team_CTF_redflag in map" );
		}
		item = BG_FindItem( "Blue Flag" );
		if ( !item || !itemRegistered[ item - bg_itemlist ] ) {
			G_Printf( S_COLOR_YELLOW "WARNING: No team_CTF_blueflag in map" );
		}
		item = BG_FindItem( "Neutral Flag" );
		if ( !item || !itemRegistered[ item - bg_itemlist ] ) {
			G_Printf( S_COLOR_YELLOW "WARNING: No team_CTF_neutralflag in map" );
		}
	}

	if( g_gametype.integer == GT_OBELISK ) {
		gentity_t	*ent;

		// check for the two obelisks
		ent = NULL;
		ent = G_Find( ent, FOFS(classname), "team_redobelisk" );
		if( !ent ) {
			G_Printf( S_COLOR_YELLOW "WARNING: No team_redobelisk in map" );
		}

		ent = NULL;
		ent = G_Find( ent, FOFS(classname), "team_blueobelisk" );
		if( !ent ) {
			G_Printf( S_COLOR_YELLOW "WARNING: No team_blueobelisk in map" );
		}
	}

	if( g_gametype.integer == GT_HARVESTER ) {
		gentity_t	*ent;

		// check for all three obelisks
		ent = NULL;
		ent = G_Find( ent, FOFS(classname), "team_redobelisk" );
		if( !ent ) {
			G_Printf( S_COLOR_YELLOW "WARNING: No team_redobelisk in map" );
		}

		ent = NULL;
		ent = G_Find( ent, FOFS(classname), "team_blueobelisk" );
		if( !ent ) {
			G_Printf( S_COLOR_YELLOW "WARNING: No team_blueobelisk in map" );
		}

		ent = NULL;
		ent = G_Find( ent, FOFS(classname), "team_neutralobelisk" );
		if( !ent ) {
			G_Printf( S_COLOR_YELLOW "WARNING: No team_neutralobelisk in map" );
		}
	}
}

/*
==============
ClearRegisteredItems
==============
*/
void ClearRegisteredItems( void ) {
	memset( itemRegistered, 0, sizeof( itemRegistered ) );

	// players always start with the base weapon
	RegisterItem( BG_FindItemForWeapon( WP_MACHINEGUN ) );
	RegisterItem( BG_FindItemForWeapon( WP_GAUNTLET ) );
	if( g_gametype.integer == GT_HARVESTER ) {
		RegisterItem( BG_FindItem( "Red Cube" ) );
		RegisterItem( BG_FindItem( "Blue Cube" ) );
	}
}

/*
===============
RegisterItem

The item will be added to the precache list
===============
*/
void RegisterItem( gitem_t *item ) {
	if ( !item ) {
		G_Error( "RegisterItem: NULL" );
	}
	itemRegistered[ item - bg_itemlist ] = qtrue;
}


/*
===============
SaveRegisteredItems

Write the needed items to a config string
so the client will know which ones to precache
===============
*/
void SaveRegisteredItems( void ) {
	char	string[MAX_ITEMS+1];
	int		i;
	int		count;

	count = 0;
	for ( i = 0 ; i < bg_numItems ; i++ ) {
		if ( itemRegistered[i] ) {
			count++;
			string[i] = '1';
		} else {
			string[i] = '0';
		}
	}
	string[ bg_numItems ] = 0;

	G_Printf( "%i items registered\n", count );
	trap_SetConfigstring(CS_ITEMS, string);
}

/*
============
G_ItemDisabled
============
*/
int G_ItemDisabled( gitem_t *item ) {

	char name[128];

	Com_sprintf(name, sizeof(name), "disable_%s", item->classname);
	return trap_Cvar_VariableIntegerValue( name );
}

/*
============
G_SpawnItem

Sets the clipping size and plants the object on the floor.

Items can't be immediately dropped to floor, because they might
be on an entity that hasn't spawned yet.
============
*/
void G_SpawnItem (gentity_t *ent, gitem_t *item) {
	G_SpawnFloat( "random", "0", &ent->random );
	G_SpawnFloat( "wait", "0", &ent->wait );

	RegisterItem( item );
	if ( G_ItemDisabled(item) )
		return;

	ent->item = item;
	// some movers spawn on the second frame, so delay item
	// spawns until the third frame so they can ride trains
	ent->nextthink = level.time + FRAMETIME * 2;
	ent->think = FinishSpawningItem;

	ent->physicsBounce = G_MatchFactoryBounceAllowed() ? 0.50f : 0.0f;	// items are bouncy when enabled

	if ( item->giType == IT_POWERUP ) {
		G_SoundIndex( "sound/items/poweruprespawn.wav" );
		G_SpawnFloat( "noglobalsound", "0", &ent->speed);
	}

	if ( item->giType == IT_PERSISTANT_POWERUP ) {
		ent->s.generic1 = ent->spawnflags;
	}
}


/*
================
G_BounceItem

================
*/
void G_BounceItem( gentity_t *ent, trace_t *trace ) {
	vec3_t	velocity;
	float	dot;
	int		hitTime;

	// reflect the velocity on the trace plane
	hitTime = level.previousTime + ( level.time - level.previousTime ) * trace->fraction;
	BG_EvaluateTrajectoryDelta( &ent->s.pos, hitTime, velocity );
	dot = DotProduct( velocity, trace->plane.normal );
	VectorMA( velocity, -2*dot, trace->plane.normal, ent->s.pos.trDelta );

	// cut the velocity to keep from bouncing forever
	VectorScale( ent->s.pos.trDelta, ent->physicsBounce, ent->s.pos.trDelta );

	// check for stop
	if ( trace->plane.normal[2] > 0 && ent->s.pos.trDelta[2] < 40 ) {
		trace->endpos[2] += 1.0;	// make sure it is off ground
		SnapVector( trace->endpos );
		G_SetOrigin( ent, trace->endpos );
		ent->s.groundEntityNum = trace->entityNum;
		return;
	}

	VectorAdd( ent->r.currentOrigin, trace->plane.normal, ent->r.currentOrigin);
	VectorCopy( ent->r.currentOrigin, ent->s.pos.trBase );
	ent->s.pos.trTime = level.time;
}


/*
================
G_RunItem

================
*/
void G_RunItem( gentity_t *ent ) {
	vec3_t		origin;
	trace_t		tr;
	int			contents;
	int			mask;

	// if groundentity has been set to -1, it may have been pushed off an edge
	if ( ent->s.groundEntityNum == -1 ) {
		if ( ent->s.pos.trType != TR_GRAVITY ) {
			ent->s.pos.trType = TR_GRAVITY;
			ent->s.pos.trTime = level.time;
		}
	}

	if ( ent->s.pos.trType == TR_STATIONARY ) {
		// check think function
		G_RunThink( ent );
		return;
	}

	// get current position
	BG_EvaluateTrajectory( &ent->s.pos, level.time, origin );

	// trace a line from the previous position to the current position
	if ( ent->clipmask ) {
		mask = ent->clipmask;
	} else {
		mask = MASK_PLAYERSOLID & ~CONTENTS_BODY;//MASK_SOLID;
	}
	trap_Trace( &tr, ent->r.currentOrigin, ent->r.mins, ent->r.maxs, origin, 
		ent->r.ownerNum, mask );

	VectorCopy( tr.endpos, ent->r.currentOrigin );

	if ( tr.startsolid ) {
		tr.fraction = 0;
	}

	trap_LinkEntity( ent );	// FIXME: avoid this for stationary?

	// check think function
	G_RunThink( ent );

	if ( tr.fraction == 1 ) {
		return;
	}

	// if it is in a nodrop volume, remove it
	contents = trap_PointContents( ent->r.currentOrigin, -1 );
	if ( contents & CONTENTS_NODROP ) {
		if (ent->item && ent->item->giType == IT_TEAM) {
			Team_FreeEntity(ent);
		} else {
			G_FreeEntity( ent );
		}
		return;
	}

	G_BounceItem( ent, &tr );
}

