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


#define	RESPAWN_ARMOR		25
#define	RESPAWN_HEALTH		35
#define	RESPAWN_AMMO		40
#define	RESPAWN_HOLDABLE	60
#define	RESPAWN_MEGAHEALTH	35//120
static const keyItemDef_t g_keyItemDefs[] = {
	{ KEY_FLAG_SILVER, "item_key_silver" },
	{ KEY_FLAG_GOLD, "item_key_gold" },
	{ KEY_FLAG_MASTER, "item_key_master" }
};
static const powerup_t g_spawnItemPowerupTags[] = {
	PW_GUARD,
	PW_DOUBLER,
	PW_AMMOREGEN,
	PW_INVULNERABILITY
};
static gentity_t *g_spawnItemPowerupSpots[4];
static int g_spawnDelayKeySeconds;
static int g_spawnDelayPowerupSeconds;

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
G_ComputeRetailSpawnDelay

Resolves Quake Live's per-level randomized key/powerup spawn delay.
===============
*/
static int G_ComputeRetailSpawnDelay( int baseDelaySeconds, int randomDelaySeconds ) {
	float	delay;

	delay = 0.0f;
	if ( baseDelaySeconds > 0 ) {
		delay = (float)baseDelaySeconds;
	}
	if ( randomDelaySeconds > 0 ) {
		delay += random() * (float)randomDelaySeconds;
	}

	return (int)( delay + 0.5f );
}

/*
===============
G_InitItemSpawnDelays

Latches the retail randomized key and map-powerup initial spawn delays once
per level so all matching entities share the same schedule.
===============
*/
void G_InitItemSpawnDelays( void ) {
	g_spawnDelayKeySeconds = G_ComputeRetailSpawnDelay( g_spawnDelay_key.integer,
		g_spawnDelayRandom_key.integer );
	g_spawnDelayPowerupSeconds = G_ComputeRetailSpawnDelay( g_spawnDelay_powerup.integer,
		g_spawnDelayRandom_powerup.integer );
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

/*
===============
G_ResetKeyItem

Restores the keyed world item for the specified bit and frees any dropped copies.
===============
*/
static gentity_t *G_ResetKeyItem( int bit ) {
	gentity_t	*ent;
	gentity_t	*result;
	gitem_t		*item;

	item = G_KeyItemForBit( bit );
	if ( !item ) {
		return NULL;
	}

	result = NULL;
	ent = NULL;
	while ( ( ent = G_Find( ent, FOFS( classname ), item->classname ) ) != NULL ) {
		if ( ent->flags & FL_DROPPED_ITEM ) {
			G_FreeEntity( ent );
			continue;
		}

		result = ent;
		RespawnItem( ent );
	}

	return result;
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
G_ItemFactorySpawnAllowed

Returns qtrue when the active factory configuration allows an item of the
specified class to spawn or be picked up.
=============
*/
static qboolean G_ItemFactorySpawnAllowed( const gitem_t *item ) {
	if ( !item ) {
		return qfalse;
	}

	switch ( item->giType ) {
	case IT_WEAPON:
		return g_factoryCvarConfig.spawnItemWeapons ? qtrue : qfalse;
	case IT_POWERUP:
		return g_factoryCvarConfig.spawnItemPowerup ? qtrue : qfalse;
	case IT_PERSISTANT_POWERUP:
		return g_runes.integer ? qtrue : qfalse;
	case IT_HOLDABLE:
		return g_factoryCvarConfig.spawnItemHoldable ? qtrue : qfalse;
	case IT_HEALTH:
		return g_factoryCvarConfig.spawnItemHealth ? qtrue : qfalse;
	case IT_ARMOR:
		return g_factoryCvarConfig.spawnItemArmor ? qtrue : qfalse;
	case IT_AMMO:
		if ( !g_factoryCvarConfig.spawnItemAmmo ) {
			return qfalse;
		}

		if ( item->giTag == WP_NUM_WEAPONS ) {
			return ( g_factoryCvarConfig.ammoPackEnabled || g_factoryCvarConfig.ammoPackHackEnabled ) ? qtrue : qfalse;
		}

		return ( g_factoryCvarConfig.ammoPackEnabled || g_factoryCvarConfig.ammoPackHackEnabled ) ? qfalse : qtrue;
	default:
		return qtrue;
	}
}

/*
=============
G_GetItemUnlockTier

Resolves the unlock tier linked to the provided item. A return value of
ITEM_UNLOCK_TIER_NONE indicates that no unlock is required.
=============
*/
static int G_GetItemUnlockTier( const gitem_t *item ) {
	weapon_t	weapon;

	if ( !item ) {
		return ITEM_UNLOCK_TIER_NONE;
	}

	if ( item->giType == IT_WEAPON ) {
		weapon = BG_WeaponForItemTag( item->giTag );

		switch ( weapon ) {
		case WP_SHOTGUN:
			return 0;
		case WP_GAUNTLET:
			return 1;
		case WP_MACHINEGUN:
			return 2;
		case WP_GRENADE_LAUNCHER:
			return 3;
		case WP_ROCKET_LAUNCHER:
			return 4;
		case WP_PLASMAGUN:
			return 5;
		case WP_RAILGUN:
			return 6;
		case WP_LIGHTNING:
			return 7;
		case WP_BFG:
			return 8;
		case WP_NAILGUN:
			return 9;
		case WP_CHAINGUN:
			return 0x0A;
		case WP_PROX_LAUNCHER:
			return 0x0B;
		case WP_GRAPPLING_HOOK:
			return 0x0E;
		case WP_HEAVY_MACHINEGUN:
			return 0x0F;
		default:
			return ITEM_UNLOCK_TIER_NONE;
		}
	}

	if ( item->giType == IT_AMMO && BG_WeaponForItemTag( item->giTag ) == WP_PROX_LAUNCHER ) {
		return 0x0D;
	}

	if ( item->giType == IT_HOLDABLE && BG_HoldableForItemTag( item->giTag ) == HI_KAMIKAZE ) {
		return 0x0C;
	}

	return ITEM_UNLOCK_TIER_NONE;
}

/*
=============
G_ClientMeetsItemUnlock

Checks whether the supplied client satisfies the unlock tier requirements
associated with an item.
=============
*/
static qboolean G_ClientMeetsItemUnlock( const gclient_t *client, const gitem_t *item ) {
	int		unlockTier;
	unsigned int	unlockFlag;

	unlockTier = G_GetItemUnlockTier( item );
	if ( unlockTier >= ITEM_UNLOCK_TIER_NONE ) {
		return qtrue;
	}

	if ( !client ) {
		return qfalse;
	}

	unlockFlag = ( unlockTier < 32 ) ? ITEM_PROGRESSION_FLAG( unlockTier ) : 0;
	if ( client->pers.progressionFlags & unlockFlag ) {
		return qtrue;
	}

	if ( client->pers.itemProgressionTier >= unlockTier ) {
		return qtrue;
	}

	if ( client->pers.itemProgressionTier + 1 >= unlockTier ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
	G_UpdateClientItemUnlockProgress

Raises the client's unlock tier and flags after a gated item has been
successfully collected.
=============
*/
static void G_UpdateClientItemUnlockProgress( gclient_t *client, const gitem_t *item ) {
	int		unlockTier;

	if ( !client ) {
		return;
	}

	unlockTier = G_GetItemUnlockTier( item );
	if ( unlockTier >= ITEM_UNLOCK_TIER_NONE || unlockTier < 0 ) {
		return;
	}

	if ( unlockTier > client->pers.itemProgressionTier ) {
		client->pers.itemProgressionTier = unlockTier;
	}

	if ( unlockTier < 32 ) {
		client->pers.progressionFlags |= ITEM_PROGRESSION_FLAG( unlockTier );
	}
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
G_SetPowerupPOITime

Mirrors the retail item-state timestamp consumed by cgame's incoming powerup POIs.
=============
*/
static void G_SetPowerupPOITime( gentity_t *ent, int markerTime ) {
	if ( !ent || !ent->item || ent->item->giType != IT_POWERUP ) {
		return;
	}

	ent->s.time = markerTime;
}

/*
=============
G_ItemUsesRespawnTimer

Returns qtrue when the item mirrors retail respawn-timer transport through
entityState_t time fields.
=============
*/
qboolean G_ItemUsesRespawnTimer( const gitem_t *item ) {
	if ( !item ) {
		return qfalse;
	}

	if ( item->giType == IT_ARMOR && item->quantity >= 25 ) {
		return qtrue;
	}

	if ( item->giType == IT_HEALTH && item->quantity >= 100 ) {
		return qtrue;
	}

	if ( item->giType == IT_POWERUP ) {
		switch ( item->giTag ) {
		case PW_QUAD:
		case PW_BATTLESUIT:
		case PW_HASTE:
		case PW_INVIS:
		case PW_REGEN:
			return qtrue;
		default:
			return qfalse;
		}
	}

	if ( item->giType == IT_HOLDABLE && BG_HoldableForItemTag( item->giTag ) == HI_MEDKIT ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
G_ShouldSendItemRespawnTimerSnapshot

Returns qtrue when a hidden item timer entity should remain snapshot-visible
after pickup, matching retail's g_itemTimers-controlled transport.
=============
*/
static qboolean G_ShouldSendItemRespawnTimerSnapshot( const gentity_t *ent, int respawnDuration ) {
	if ( respawnDuration <= 0 ) {
		return qfalse;
	}

	if ( g_itemTimers.integer == 0 ) {
		return qfalse;
	}

	if ( !ent || !ent->item || ent->item->quantity == 0 ) {
		return qfalse;
	}

	return G_ItemUsesRespawnTimer( ent->item );
}

/*
=============
G_SetItemRespawnTimerState

Publishes the retail respawn deadline and duration consumed by cgame's world
item timer helper.
=============
*/
static void G_SetItemRespawnTimerState( gentity_t *ent, int markerTime, int respawnDuration ) {
	if ( !ent || !G_ItemUsesRespawnTimer( ent->item ) ) {
		return;
	}

	if ( respawnDuration < 0 ) {
		respawnDuration = 0;
	}

	ent->s.time = markerTime;
	ent->s.time2 = respawnDuration;
	ent->s.retailEventData = ent->team ? 1 : 0;
	if ( G_ShouldSendItemRespawnTimerSnapshot( ent, respawnDuration ) ) {
		ent->r.svFlags &= ~SVF_NOCLIENT;
	}
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

/*
=============
G_SpawnItemPowerupSlot

Maps the retail random persistant-powerup set onto the tracked spawn slots used
to avoid reusing the same spawn point for multiple active entries.
=============
*/
static int G_SpawnItemPowerupSlot( powerup_t powerup ) {
	int	i;

	for ( i = 0; i < ARRAY_LEN( g_spawnItemPowerupTags ); i++ ) {
		if ( g_spawnItemPowerupTags[i] == powerup ) {
			return i;
		}
	}

	return -1;
}

/*
=============
G_SpawnItemPowerupSpawnflags

Builds the persistant-powerup team restriction bits used by
BG_CanGrabPersistantPowerupItem.
=============
*/
static int G_SpawnItemPowerupSpawnflags( team_t preferredTeam ) {
	switch ( preferredTeam ) {
	case TEAM_RED:
		return 2;
	case TEAM_BLUE:
		return 4;
	default:
		return 0;
	}
}

/*
=============
G_SpawnItemPowerupSpawnClassname

Chooses the retail spawn-point class used for dynamic persistant powerups.
=============
*/
static const char *G_SpawnItemPowerupSpawnClassname( team_t preferredTeam ) {
	switch ( preferredTeam ) {
	case TEAM_RED:
		return "team_CTF_redspawn";
	case TEAM_BLUE:
		return "team_CTF_bluespawn";
	default:
		return "info_player_deathmatch";
	}
}

/*
=============
G_SpawnItemPowerup

Spawns one of the retail random persistant powerups on an eligible spawn point.
=============
*/
static gentity_t *G_SpawnItemPowerup( powerup_t powerup, team_t preferredTeam ) {
	gentity_t	*spot;
	gentity_t	*spawned;
	gentity_t	*candidates[16];
	gitem_t		*item;
	const char	*classname;
	int		slotIndex;
	int		candidateCount;
	int		i;

	if ( !g_runes.integer ) {
		return NULL;
	}

	classname = G_SpawnItemPowerupSpawnClassname( preferredTeam );
	slotIndex = G_SpawnItemPowerupSlot( powerup );
	spot = NULL;
	candidateCount = 0;

	while ( candidateCount < ARRAY_LEN( candidates ) &&
		( spot = G_Find( spot, FOFS( classname ), classname ) ) != NULL ) {
		qboolean	occupied;

		occupied = qfalse;
		if ( slotIndex >= 0 ) {
			for ( i = 0; i < ARRAY_LEN( g_spawnItemPowerupSpots ); i++ ) {
				if ( g_spawnItemPowerupSpots[i] == spot ) {
					occupied = qtrue;
					break;
				}
			}
		}

		if ( occupied ) {
			continue;
		}

		candidates[candidateCount++] = spot;
	}

	if ( !candidateCount ) {
		return NULL;
	}

	spot = candidates[rand() % candidateCount];
	if ( slotIndex >= 0 ) {
		g_spawnItemPowerupSpots[slotIndex] = spot;
	}

	item = BG_FindItemForPowerup( powerup );
	if ( !item ) {
		G_Error( "G_SpawnItemPowerup: missing powerup %i", powerup );
	}

	RegisterItem( item );

	spawned = G_Spawn();
	spawned->s.eType = ET_ITEM;
	spawned->s.modelindex = ITEM_INDEX( item );
	spawned->s.modelindex2 = 0;
	spawned->classname = item->classname;
	spawned->item = item;
	VectorSet( spawned->r.mins, -ITEM_RADIUS, -ITEM_RADIUS, -ITEM_RADIUS );
	VectorSet( spawned->r.maxs, ITEM_RADIUS, ITEM_RADIUS, ITEM_RADIUS );
	spawned->r.contents = CONTENTS_TRIGGER;
	spawned->touch = Touch_Item;
	spawned->physicsBounce = G_MatchFactoryBounceAllowed() ? 0.50f : 0.0f;
	spawned->spawnflags = G_SpawnItemPowerupSpawnflags( preferredTeam );
	spawned->s.generic1 = spawned->spawnflags;
	G_SetOrigin( spawned, spot->s.origin );
	spawned->s.pos.trType = TR_GRAVITY;
	spawned->s.pos.trTime = level.time;
	VectorClear( spawned->s.pos.trDelta );
	spawned->s.groundEntityNum = ENTITYNUM_NONE;
	trap_LinkEntity( spawned );

	return spawned;
}

/*
=============
G_RespawnItemPowerup

Respawns a dropped retail persistant powerup at a fresh eligible spawn point.
=============
*/
static void G_RespawnItemPowerup( gentity_t *ent ) {
	powerup_t	powerup;
	team_t		preferredTeam;

	if ( !ent || !ent->item ) {
		return;
	}

	powerup = (powerup_t)ent->item->giTag;
	if ( level.redSpawnPointCount >= 5 && level.blueSpawnPointCount >= 5 ) {
		preferredTeam = ( rand() & 1 ) ? TEAM_RED : TEAM_BLUE;
	} else {
		preferredTeam = TEAM_FREE;
	}

	G_FreeEntity( ent );
	if ( !g_runes.integer ) {
		return;
	}

	G_SpawnItemPowerup( powerup, preferredTeam );
}

/*
=============
G_SpawnItemPowerups

Seeds the retail random persistant-powerup set during level init.
=============
*/
void G_SpawnItemPowerups( void ) {
	team_t	preferredTeam;
	int		i;

	memset( g_spawnItemPowerupSpots, 0, sizeof( g_spawnItemPowerupSpots ) );

	if ( !g_runes.integer ) {
		return;
	}

	if ( g_gametype.integer == GT_SINGLE_PLAYER ) {
		return;
	}

	if ( level.redSpawnPointCount >= 5 && level.blueSpawnPointCount >= 5 ) {
		preferredTeam = ( rand() & 1 ) ? TEAM_RED : TEAM_BLUE;
	} else {
		if ( level.deathmatchSpawnPointCount < 5 ) {
			G_Printf( "WARNING: not enough available spawn points for spawned persistant powerups\n" );
			return;
		}

		preferredTeam = TEAM_FREE;
	}

	for ( i = 0; i < ARRAY_LEN( g_spawnItemPowerupTags ); i++ ) {
		G_SpawnItemPowerup( g_spawnItemPowerupTags[i], preferredTeam );

		if ( preferredTeam == TEAM_RED ) {
			preferredTeam = TEAM_BLUE;
		} else if ( preferredTeam == TEAM_BLUE ) {
			preferredTeam = TEAM_RED;
		}
	}
}

/*
=============
G_RecordTeamPickupStat

Increments a per-client pickup counter used for team aggregate scoreboard stats.
=============
*/
static void G_RecordTeamPickupStat( gentity_t *player, teamScoreStatIndex_t statIndex ) {
	if ( !player || !player->client ) {
		return;
	}

	if ( statIndex < 0 || statIndex >= TEAMSTAT_COUNT ) {
		return;
	}

	player->client->pers.teamScoreStats[statIndex]++;
}

/*
=============
G_RecordPlacementPickupTelemetry

Updates per-player pickup count and interval timing for placement ownerdraw stats.
=============
*/
static void G_RecordPlacementPickupTelemetry( gentity_t *player, scorestatPickupIndex_t pickupIndex ) {
	int now;
	int lastTime;
	int interval;

	if ( !player || !player->client ) {
		return;
	}

	if ( pickupIndex < 0 || pickupIndex >= SCORESTAT_PICKUP_COUNT ) {
		return;
	}

	now = level.time;
	lastTime = player->client->pers.pickupLastTime[pickupIndex];
	if ( lastTime > 0 && now > lastTime ) {
		interval = now - lastTime;
		player->client->pers.pickupIntervalTotalMs[pickupIndex] += interval;
		player->client->pers.pickupIntervalCount[pickupIndex]++;
	}

	player->client->pers.pickupLastTime[pickupIndex] = now;
}

/*
=============
G_RecordRetailPickupStat

Increments one retail PLAYER_STATS pickup bucket mirrored in writable source.
=============
*/
static void G_RecordRetailPickupStat( gentity_t *player, rankPickupStat_t pickupStat ) {
	if ( !player || !player->client ) {
		return;
	}

	if ( pickupStat < 0 || pickupStat >= RANK_PICKUP_COUNT ) {
		return;
	}

	player->client->pers.rankPickupCounts[pickupStat]++;
}

/*
=============
G_RecordRetailPickupStats

Tracks the broader retail PLAYER_STATS pickup taxonomy alongside the existing
team-score and ownerdraw telemetry.
=============
*/
static void G_RecordRetailPickupStats( gentity_t *player, const gentity_t *ent ) {
	const gitem_t	*item;
	rankPickupStat_t	pickupStat;
	holdable_t		holdable;

	if ( !player || !player->client || !ent || !ent->item ) {
		return;
	}

	item = ent->item;
	switch ( item->giType ) {
	case IT_ARMOR:
		G_RecordRetailPickupStat( player, RANK_PICKUP_ARMOR );
		if ( item->classname && !Q_stricmp( item->classname, "item_armor_body" ) ) {
			G_RecordRetailPickupStat( player, RANK_PICKUP_RED_ARMOR );
		} else if ( item->classname && !Q_stricmp( item->classname, "item_armor_combat" ) ) {
			G_RecordRetailPickupStat( player, RANK_PICKUP_YELLOW_ARMOR );
		} else if ( item->classname && !Q_stricmp( item->classname, "item_armor_jacket" ) ) {
			G_RecordRetailPickupStat( player, RANK_PICKUP_GREEN_ARMOR );
		}
		break;

	case IT_HEALTH:
		G_RecordRetailPickupStat( player, RANK_PICKUP_HEALTH );
		if ( item->classname && !Q_stricmp( item->classname, "item_health_mega" ) ) {
			G_RecordRetailPickupStat( player, RANK_PICKUP_MEGA_HEALTH );
		}
		break;

	case IT_POWERUP:
		pickupStat = RANK_PICKUP_OTHER_POWERUP;
		switch ( item->giTag ) {
		case PW_QUAD:
			pickupStat = RANK_PICKUP_QUAD;
			break;
		case PW_BATTLESUIT:
			pickupStat = RANK_PICKUP_BATTLESUIT;
			break;
		case PW_HASTE:
			pickupStat = RANK_PICKUP_HASTE;
			break;
		case PW_INVIS:
			pickupStat = RANK_PICKUP_INVIS;
			break;
		case PW_REGEN:
			pickupStat = RANK_PICKUP_REGEN;
			break;
		case PW_FLIGHT:
			pickupStat = RANK_PICKUP_FLIGHT;
			break;
		case PW_INVULNERABILITY:
			pickupStat = RANK_PICKUP_INVULNERABILITY;
			break;
		default:
			break;
		}
		G_RecordRetailPickupStat( player, pickupStat );
		break;

	case IT_PERSISTANT_POWERUP:
		pickupStat = RANK_PICKUP_OTHER_POWERUP;
		switch ( item->giTag ) {
		case PW_SCOUT:
			pickupStat = RANK_PICKUP_SCOUT;
			break;
		case PW_GUARD:
			pickupStat = RANK_PICKUP_GUARD;
			break;
		case PW_DOUBLER:
			pickupStat = RANK_PICKUP_DOUBLER;
			break;
		case PW_AMMOREGEN:
			pickupStat = RANK_PICKUP_ARMOR_REGEN;
			break;
		default:
			break;
		}
		G_RecordRetailPickupStat( player, pickupStat );
		break;

	case IT_HOLDABLE:
		holdable = BG_HoldableForItemTag( item->giTag );
		pickupStat = RANK_PICKUP_OTHER_HOLDABLE;
		switch ( holdable ) {
		case HI_TELEPORTER:
			pickupStat = RANK_PICKUP_TELEPORTER;
			break;
		case HI_MEDKIT:
			pickupStat = RANK_PICKUP_MEDKIT;
			break;
		case HI_KAMIKAZE:
			pickupStat = RANK_PICKUP_KAMIKAZE;
			break;
		case HI_PORTAL:
			pickupStat = RANK_PICKUP_PORTAL;
			break;
		case HI_INVULNERABILITY:
			pickupStat = RANK_PICKUP_INVULNERABILITY;
			break;
		default:
			break;
		}
		G_RecordRetailPickupStat( player, pickupStat );
		break;

	case IT_TEAM:
		switch ( item->giTag ) {
		case PW_REDFLAG:
			G_RecordRetailPickupStat( player, RANK_PICKUP_RED_FLAG );
			break;
		case PW_BLUEFLAG:
			G_RecordRetailPickupStat( player, RANK_PICKUP_BLUE_FLAG );
			break;
		case PW_NEUTRALFLAG:
			G_RecordRetailPickupStat( player, RANK_PICKUP_NEUTRAL_FLAG );
			break;
		default:
			break;
		}
		break;

	default:
		break;
	}
}

/*
=============
G_GetTeamPickupStatForItem

Classifies an item entity into a team pickup stat bucket when applicable.
=============
*/
static qboolean G_GetTeamPickupStatForItem( const gentity_t *ent, teamScoreStatIndex_t *statIndex ) {
	const gitem_t	*item;

	if ( !ent || !ent->item || !statIndex ) {
		return qfalse;
	}

	item = ent->item;
	if ( !item->classname ) {
		return qfalse;
	}

	switch ( item->giType ) {
	case IT_ARMOR:
		if ( !Q_stricmp( item->classname, "item_armor_body" ) ) {
			*statIndex = TEAMSTAT_PICKUPS_RA;
			return qtrue;
		}
		if ( !Q_stricmp( item->classname, "item_armor_combat" ) ) {
			*statIndex = TEAMSTAT_PICKUPS_YA;
			return qtrue;
		}
		if ( !Q_stricmp( item->classname, "item_armor_jacket" ) ) {
			*statIndex = TEAMSTAT_PICKUPS_GA;
			return qtrue;
		}
		return qfalse;
	case IT_HEALTH:
		if ( !Q_stricmp( item->classname, "item_health_mega" ) ) {
			*statIndex = TEAMSTAT_PICKUPS_MH;
			return qtrue;
		}
		return qfalse;
	case IT_POWERUP:
		switch ( item->giTag ) {
		case PW_QUAD:
			*statIndex = TEAMSTAT_PICKUPS_QUAD;
			return qtrue;
		case PW_BATTLESUIT:
			*statIndex = TEAMSTAT_PICKUPS_BS;
			return qtrue;
		case PW_REGEN:
			*statIndex = TEAMSTAT_PICKUPS_REGEN;
			return qtrue;
		case PW_HASTE:
			*statIndex = TEAMSTAT_PICKUPS_HASTE;
			return qtrue;
		case PW_INVIS:
			*statIndex = TEAMSTAT_PICKUPS_INVIS;
			return qtrue;
		default:
			return qfalse;
		}
	case IT_HOLDABLE:
		if ( BG_HoldableForItemTag( item->giTag ) == HI_MEDKIT ) {
			*statIndex = TEAMSTAT_PICKUPS_MEDKIT;
			return qtrue;
		}
		return qfalse;
	case IT_TEAM:
		if ( item->giTag == PW_REDFLAG || item->giTag == PW_BLUEFLAG || item->giTag == PW_NEUTRALFLAG ) {
			*statIndex = TEAMSTAT_PICKUPS_FLAG;
			return qtrue;
		}
		return qfalse;
	default:
		return qfalse;
	}
}

/*
=============
G_GetPlacementPickupIndexForItem

Maps pickup entities that drive 1st/2nd place pickup timing ownerdraws.
=============
*/
static qboolean G_GetPlacementPickupIndexForItem( const gentity_t *ent, scorestatPickupIndex_t *pickupIndex ) {
	teamScoreStatIndex_t teamStatIndex;

	if ( !pickupIndex ) {
		return qfalse;
	}

	if ( !G_GetTeamPickupStatForItem( ent, &teamStatIndex ) ) {
		return qfalse;
	}

	switch ( teamStatIndex ) {
	case TEAMSTAT_PICKUPS_RA:
		*pickupIndex = SCORESTAT_PICKUP_RA;
		return qtrue;
	case TEAMSTAT_PICKUPS_YA:
		*pickupIndex = SCORESTAT_PICKUP_YA;
		return qtrue;
	case TEAMSTAT_PICKUPS_GA:
		*pickupIndex = SCORESTAT_PICKUP_GA;
		return qtrue;
	case TEAMSTAT_PICKUPS_MH:
		*pickupIndex = SCORESTAT_PICKUP_MH;
		return qtrue;
	default:
		return qfalse;
	}
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

/*
=============
G_ResetPowerupFragCount

Clears the retail frag counter paired with a newly started timed powerup.
=============
*/
static void G_ResetPowerupFragCount( gclient_t *client, int powerup ) {
	if ( !client ) {
		return;
	}

	switch ( powerup ) {
	case PW_QUAD:
		client->ps.stats[STAT_QUAD_FRAG_COUNT] = 0;
		break;
	case PW_BATTLESUIT:
		client->ps.stats[STAT_BATTLESUIT_FRAG_COUNT] = 0;
		break;
	default:
		break;
	}
}

/*
=============
Pickup_Powerup

Applies retail timed powerup pickup state and side effects.
=============
*/
int Pickup_Powerup( gentity_t *ent, gentity_t *other ) {
	int			quantity;
	int			i;
	int			powerup;
	gclient_t	*client;

	powerup = ent->item->giTag;

	if ( !other->client->ps.powerups[powerup] ) {
		G_ResetPowerupFragCount( other->client, powerup );

		// round timing to seconds to make multiple powerup timers
		// count in sync
		other->client->ps.powerups[powerup] =
			level.time - ( level.time % 1000 );
	}

	if ( ent->count ) {
		quantity = ent->count;
	} else {
		quantity = ent->item->quantity;
	}

	other->client->ps.powerups[powerup] += quantity * 1000;

	{
		teamScoreStatIndex_t holdStatIndex;

		holdStatIndex = G_TeamHoldStatForPowerup( powerup );
		if ( holdStatIndex >= 0 && holdStatIndex < TEAMSTAT_COUNT ) {
			G_FlushExpiredClientTeamHoldStats( other->client, level.time );
			G_BeginClientTeamHoldStat( other->client, holdStatIndex );
		}
	}

	if ( powerup == PW_QUAD ) {
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

/*
=============
G_FindPersistantPowerupFlagBase

Resolves the home-base flag entity for the requested team item classname.
=============
*/
static gentity_t *G_FindPersistantPowerupFlagBase( const char *classname ) {
	gentity_t	*flag;

	flag = NULL;
	while ( ( flag = G_Find( flag, FOFS( classname ), classname ) ) != NULL ) {
		if ( !( flag->flags & FL_DROPPED_ITEM ) ) {
			return flag;
		}
	}

	return NULL;
}

/*
=============
G_PersistantPowerupColorPrefix

Uses the nearest CTF base flag to mirror retail pickup message coloring.
=============
*/
static const char *G_PersistantPowerupColorPrefix( gentity_t *ent ) {
	gentity_t	*redFlag;
	gentity_t	*blueFlag;

	if ( !ent || g_gametype.integer < GT_TEAM ) {
		return S_COLOR_WHITE;
	}

	redFlag = G_FindPersistantPowerupFlagBase( "team_CTF_redflag" );
	blueFlag = G_FindPersistantPowerupFlagBase( "team_CTF_blueflag" );
	if ( !redFlag && !blueFlag ) {
		return S_COLOR_WHITE;
	}
	if ( !redFlag ) {
		return S_COLOR_BLUE;
	}
	if ( !blueFlag ) {
		return S_COLOR_RED;
	}

	return ( DistanceSquared( ent->r.currentOrigin, redFlag->r.currentOrigin ) <=
		DistanceSquared( ent->r.currentOrigin, blueFlag->r.currentOrigin ) ) ? S_COLOR_RED : S_COLOR_BLUE;
}

/*
=============
G_AnnouncePersistantPowerupPickup

Restores the retail pickup banner for spawned persistant powerups.
=============
*/
static void G_AnnouncePersistantPowerupPickup( gentity_t *ent, gentity_t *other ) {
	const char	*pickupName;
	const char	*colorPrefix;

	if ( !ent || !ent->item || !other || !other->client ) {
		return;
	}

	if ( ent->flags & FL_DROPPED_ITEM ) {
		return;
	}

	pickupName = ent->item->pickup_name ? ent->item->pickup_name : ent->item->classname;
	if ( !pickupName || !pickupName[0] ) {
		return;
	}

	colorPrefix = G_PersistantPowerupColorPrefix( ent );
	trap_SendServerCommand( -1,
		va( "print \"%s%s got the %s!^7\n\"", colorPrefix, other->client->pers.netname, pickupName ) );
}

int Pickup_PersistantPowerup( gentity_t *ent, gentity_t *other ) {
	other->client->ps.stats[STAT_PERSISTANT_POWERUP] = ITEM_INDEX( ent->item );
	other->client->persistantPowerup = ent;
	other->client->ps.powerups[ent->item->giTag] = INT_MAX;
	G_AnnouncePersistantPowerupPickup( ent, other );

	return -1;
}

//======================================================================

int Pickup_Holdable( gentity_t *ent, gentity_t *other ) {
	other->client->ps.stats[STAT_HOLDABLE_ITEM] = ent->item - bg_itemlist;

	if ( BG_HoldableForItemTag( ent->item->giTag ) == HI_KAMIKAZE ) {
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
		other->client->ps.stats[STAT_KEY_MASK] = other->keyMask;
	}
	G_BroadcastClientKeyMask( other->s.number );

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
Add_Ammo

Adds ammo to the supplied client while clamping to the configured maximum.
=============
*/
void Add_Ammo (gentity_t *ent, int weapon, int count)
{
	weapon_t	weaponIndex;
	int		maxStack;
	int		defaultPack;
	int		ammoPackCount;
	int		ownedWeapon;

	if ( !ent || !ent->client ) {
		return;
	}

	weaponIndex = (weapon_t)weapon;
	if ( weaponIndex == WP_NUM_WEAPONS ) {
		for ( ownedWeapon = WP_MACHINEGUN; ownedWeapon < WP_NUM_WEAPONS; ownedWeapon++ ) {
			if ( !( ent->client->ps.stats[STAT_WEAPONS] & ( 1 << ownedWeapon ) ) ) {
				continue;
			}

			ammoPackCount = G_GetAmmoPackPickupCount( (weapon_t)ownedWeapon, 0 );
			if ( ammoPackCount <= 0 ) {
				continue;
			}

			Add_Ammo( ent, ownedWeapon, ammoPackCount );
		}

		return;
	}

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

	quantity = ent->count;
	if ( quantity == 0 ) {
		quantity = ent->item->quantity;
	}

	Add_Ammo( other, BG_WeaponForItemTag( ent->item->giTag ), quantity );

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

	weapon = ent->item ? BG_WeaponForItemTag( ent->item->giTag ) : WP_NONE;

	if ( g_weaponRespawn.integer == 0 && !( ent->flags & FL_DROPPED_ITEM )
		&& weapon > WP_NONE && weapon < WP_NUM_WEAPONS
		&& ( other->client->ps.stats[STAT_WEAPONS] & ( 1 << weapon ) )
		&& other->client->ps.ammo[weapon] != 0 ) {
		return 0;
	}

	if ( ent->count < 0 ) {
		Com_Error( ERR_DROP, "Pickup_Weapon: item has infinite ammo" );
	}

	quantity = ent->count;
	if ( quantity == 0 ) {
		quantity = ent->item->quantity;
	}

	if ( quantity < 0 ) {
		quantity = 0;
	}

	// add the weapon
	other->client->ps.stats[STAT_WEAPONS] |= ( 1 << weapon );

	Add_Ammo( other, weapon, quantity );

	if ( g_weaponRespawn.integer == 0 && !( ent->flags & FL_DROPPED_ITEM )
		&& weapon > WP_NONE && weapon < WP_NUM_WEAPONS && ent->item ) {
		other->client->ps.ammo[weapon] = ent->item->quantity;
	}

	if ( weapon == WP_GRAPPLING_HOOK ) {
		other->client->ps.ammo[weapon] = -1; // unlimited ammo
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

Adds armor from pickups and clamps it through the shared retail armor rules.
=============
*/
int Pickup_Armor( gentity_t *ent, gentity_t *other ) {
	playerState_t	*ps;
	qboolean	armorTiered;

	if ( !other || !other->client ) {
		return RESPAWN_ARMOR;
	}

	ps = &other->client->ps;
	armorTiered = g_armorTiered.integer ? qtrue : qfalse;
	BG_ApplyArmorPickup( ps, ent ? ent->item : NULL, armorTiered );

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

	ent->spectatorItemPickupClientNum = 0;
	ent->spectatorItemPickupPalette = 0;
	ent->spectatorItemPickupLayoutOrder = 0;
	ent->r.contents = CONTENTS_TRIGGER;
	ent->s.eFlags &= ~EF_NODRAW;
	ent->r.svFlags &= ~SVF_NOCLIENT;
	G_SetPowerupPOITime( ent, level.time );
	G_SetItemRespawnTimerState( ent, level.time, 0 );
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

	if ( ent->item->giType == IT_HOLDABLE && BG_HoldableForItemTag( ent->item->giTag ) == HI_KAMIKAZE ) {
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
G_IsSpectatorItemPickupItem

Returns qtrue for the major-item classes used by the retail spectator timer
overlay.
===============
*/
static qboolean G_IsSpectatorItemPickupItem( const gitem_t *item ) {
	if ( !item ) {
		return qfalse;
	}

	if ( item->giType == IT_POWERUP ) {
		return qtrue;
	}

	if ( item->giType == IT_HEALTH && item->quantity >= 100 ) {
		return qtrue;
	}

	if ( item->giType == IT_ARMOR && item->quantity >= 50 ) {
		return qtrue;
	}

	return qfalse;
}

/*
===============
G_GetSpectatorItemPickupPalette

Picks the compact retail palette id used by the spectator pickup overlay.
===============
*/
static int G_GetSpectatorItemPickupPalette( const gentity_t *player ) {
	int	rank;

	if ( !player || !player->client ) {
		return 0;
	}

	if ( g_gametype.integer == GT_TOURNAMENT ) {
		rank = player->client->ps.persistant[PERS_RANK] & ~RANK_TIED_FLAG;
		if ( rank == 0 ) {
			return 1;
		}

		if ( rank == 1 ) {
			return 2;
		}
	}

	if ( player->client->sess.sessionTeam == TEAM_RED ) {
		return 1;
	}

	if ( player->client->sess.sessionTeam == TEAM_BLUE ) {
		return 2;
	}

	return 0;
}

/*
===============
G_GetSpectatorItemPickupLayoutOrder

Builds the duel-side ordering hint consumed by the retail spectator overlay.
===============
*/
static int G_GetSpectatorItemPickupLayoutOrder( const gentity_t *player ) {
	int	rank;

	if ( !player || !player->client || g_gametype.integer != GT_TOURNAMENT ) {
		return 0;
	}

	rank = player->client->ps.persistant[PERS_RANK] & ~RANK_TIED_FLAG;
	if ( rank < 0 ) {
		rank = 0;
	}

	return rank + 1;
}

/*
===============
G_IsSpectatorItemSyncClient

Returns qtrue when the requested client is an active spectator observer.
===============
*/
static qboolean G_IsSpectatorItemSyncClient( int clientNum ) {
	gentity_t	*ent;

	if ( clientNum < 0 || clientNum >= level.maxclients ) {
		return qfalse;
	}

	ent = &g_entities[clientNum];
	if ( !ent->inuse || !ent->client || ent->client->pers.connected != CON_CONNECTED ) {
		return qfalse;
	}

	return ( qboolean )( ent->client->sess.sessionTeam == TEAM_SPECTATOR );
}

/*
===============
G_SendSpectatorItemStateToClient

Builds the synthetic spectator timer event for one spectator client.
===============
*/
static void G_SendSpectatorItemStateToClient( int clientNum, gentity_t *itemEnt, qboolean initialSync ) {
	gentity_t	*te;

	if ( !G_IsSpectatorItemSyncClient( clientNum ) ) {
		return;
	}

	if ( !itemEnt || !itemEnt->item || !G_IsSpectatorItemPickupItem( itemEnt->item ) ) {
		return;
	}

	if ( ( itemEnt->flags & FL_DROPPED_ITEM ) || itemEnt->nextthink <= level.time ||
		itemEnt->r.contents != 0 || !( itemEnt->s.eFlags & EF_NODRAW ) ) {
		return;
	}

	if ( itemEnt->spectatorItemPickupClientNum <= 0 ||
		itemEnt->spectatorItemPickupClientNum > level.maxclients ) {
		return;
	}

	te = G_TempEntity( itemEnt->s.pos.trBase, EV_ITEM_PICKUP_SPEC );
	te->r.svFlags |= SVF_SINGLECLIENT;
	te->r.singleClient = clientNum;
	te->s.groundEntityNum = itemEnt->spectatorItemPickupClientNum;
	te->s.constantLight = itemEnt->spectatorItemPickupPalette;
	te->s.origin[0] = (float)itemEnt->nextthink;
	te->s.origin[1] = (float)( g_gametype.integer == GT_TOURNAMENT );
	te->s.clientNum = itemEnt->s.modelindex;
	te->s.frame = itemEnt->spectatorItemPickupLayoutOrder;
	te->s.loopSound = initialSync ? 1 : 0;
	te->s.modelindex2 = 0;
}

/*
===============
G_BroadcastSpectatorItemState

Pushes the synthetic spectator timer event to all connected spectators.
===============
*/
static void G_BroadcastSpectatorItemState( gentity_t *itemEnt ) {
	int	i;

	if ( !itemEnt || !itemEnt->item || !G_IsSpectatorItemPickupItem( itemEnt->item ) ) {
		return;
	}

	for ( i = 0; i < level.maxclients; i++ ) {
		G_SendSpectatorItemStateToClient( i, itemEnt, qfalse );
	}
}

/*
===============
G_SyncSpectatorItemStatesForClient

Resends live spectator item timers to one client entering observer mode.
===============
*/
void G_SyncSpectatorItemStatesForClient( int clientNum ) {
	int	i;

	if ( !G_IsSpectatorItemSyncClient( clientNum ) ) {
		return;
	}

	for ( i = level.maxclients; i < level.num_entities; i++ ) {
		G_SendSpectatorItemStateToClient( clientNum, &g_entities[i], qtrue );
	}
}

/*
===============
G_RecordSpectatorItemPickup

Publishes the synthetic retail major-item pickup event consumed by the
spectator timer overlay.
===============
*/
static void G_RecordSpectatorItemPickup( gentity_t *itemEnt, gentity_t *player, int respawn ) {
	if ( !itemEnt || !player || !player->client ) {
		return;
	}

	if ( respawn <= 0 || ( itemEnt->flags & FL_DROPPED_ITEM ) ) {
		return;
	}

	if ( !G_IsSpectatorItemPickupItem( itemEnt->item ) ) {
		return;
	}

	itemEnt->spectatorItemPickupClientNum = player->s.number + 1;
	itemEnt->spectatorItemPickupPalette = G_GetSpectatorItemPickupPalette( player );
	itemEnt->spectatorItemPickupLayoutOrder = G_GetSpectatorItemPickupLayoutOrder( player );
}


/*
===============
G_SyncWeaponRespawnCvarForItem

Keeps the retail weapon-stay CVar mirror current before shared grab and pickup
code read it.
===============
*/
static void G_SyncWeaponRespawnCvarForItem( const gitem_t *item ) {
	if ( !item || item->giType != IT_WEAPON ) {
		return;
	}

	// Cvar_Update may otherwise skip a stale mirror with a matching mod count.
	g_weaponRespawn.modificationCount = -1;
	trap_Cvar_Update( &g_weaponRespawn );
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

	if ( !G_ItemFactorySpawnAllowed( ent->item ) ) {
		return;
	}

	if ( !G_ClientMeetsItemUnlock( other->client, ent->item ) ) {
		other->client->ps.persistant[PERS_PLAYEREVENTS] ^= PLAYEREVENT_DENIEDREWARD;
		return;
	}

	G_SyncWeaponRespawnCvarForItem( ent->item );

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

	{
		teamScoreStatIndex_t	teamStatIndex;
		scorestatPickupIndex_t	pickupIndex;

		if ( G_GetTeamPickupStatForItem( ent, &teamStatIndex ) ) {
			G_RecordTeamPickupStat( other, teamStatIndex );
		}
		if ( G_GetPlacementPickupIndexForItem( ent, &pickupIndex ) ) {
			G_RecordPlacementPickupTelemetry( other, pickupIndex );
		}
		G_RecordRetailPickupStats( other, ent );
	}

	G_UpdateClientItemUnlockProgress( other->client, ent->item );

	// play the normal pickup sound
	if (predict) {
		G_AddPredictableEvent( other, EV_ITEM_PICKUP, ent->s.modelindex );
	} else {
		G_AddEvent( other, EV_ITEM_PICKUP, ent->s.modelindex );
	}

	// powerup and team pickups are global broadcasts
	if ( ent->item->giType == IT_POWERUP || ent->item->giType == IT_TEAM ) {
		// if we want the global sound to play
		if (!ent->speed) {
			gentity_t	*te;

			te = G_TempEntity( ent->s.pos.trBase, EV_GLOBAL_ITEM_PICKUP );
			te->s.eventParm = ent->s.modelindex;
			te->s.groundEntityNum = other->s.number;
			te->r.svFlags |= SVF_BROADCAST;
		} else {
			gentity_t	*te;

			te = G_TempEntity( ent->s.pos.trBase, EV_GLOBAL_ITEM_PICKUP );
			te->s.eventParm = ent->s.modelindex;
			te->s.groundEntityNum = other->s.number;
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
		G_SetPowerupPOITime( ent, level.time );
		G_SetItemRespawnTimerState( ent, level.time, 0 );
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

	G_RecordSpectatorItemPickup( ent, other, respawn );

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
	G_SetItemRespawnTimerState( ent, ( respawn > 0 ) ? ent->nextthink : level.time,
		( respawn > 0 ) ? respawn * 1000 : 0 );
	if ( ent->item->giType == IT_POWERUP ) {
		G_SetPowerupPOITime( ent, ( respawn > 0 ) ? ent->nextthink : level.time );
	}
	trap_LinkEntity( ent );
	G_BroadcastSpectatorItemState( ent );
}


//======================================================================

/*
=================
G_DroppedPowerupTouchCaptureZone

Routes dropped powerup capture-zone contacts through the retail flag capture
path when a client-backed owner is available.
=================
*/
static int G_DroppedPowerupTouchCaptureZone( gentity_t *trigger, gentity_t *ent ) {
	const char	*flagClassname;
	int		team;
	gentity_t	*other;
	gentity_t	*flag;

	if ( !trigger || !ent || !trigger->team ) {
		return 0;
	}

	if ( !Q_stricmp( trigger->team, "red" ) ) {
		team = TEAM_RED;
		flagClassname = "team_CTF_redflag";
	} else if ( !Q_stricmp( trigger->team, "blue" ) ) {
		team = TEAM_BLUE;
		flagClassname = "team_CTF_blueflag";
	} else {
		return 0;
	}

	other = ent;
	if ( !other->client && other->parent && other->parent->client ) {
		other = other->parent;
	}
	if ( !other->client ) {
		return 0;
	}

	flag = NULL;
	while ( ( flag = G_Find( flag, FOFS( classname ), flagClassname ) ) != NULL ) {
		if ( flag->flags & FL_DROPPED_ITEM ) {
			continue;
		}

		return Team_TouchOurFlag( flag, other, team );
	}

	return 0;
}

/*
=================
G_DroppedPowerupRunFrame

Mirrors the retail dropped-powerup trigger bridge for jump pads, teleporters,
and capture zones.
=================
*/
static void G_DroppedPowerupRunFrame( gentity_t *ent, float thinktime ) {
	int			i;
	int			num;
	int			touch[MAX_GENTITIES];
	vec3_t		mins;
	vec3_t		maxs;

	(void)thinktime;

	if ( !ent->item || ent->item->giType != IT_POWERUP ) {
		return;
	}

	VectorSet( mins,
		ent->r.currentOrigin[0] - 15.0f,
		ent->r.currentOrigin[1] - 15.0f,
		ent->r.currentOrigin[2] - 15.0f );
	VectorSet( maxs,
		ent->r.currentOrigin[0] + 15.0f,
		ent->r.currentOrigin[1] + 15.0f,
		ent->r.currentOrigin[2] + 15.0f );

	num = trap_EntitiesInBox( mins, maxs, touch, MAX_GENTITIES );
	for ( i = 0; i < num; i++ ) {
		gentity_t	*trigger;

		trigger = &g_entities[touch[i]];
		if ( trigger == ent || !trigger->inuse || !trigger->classname ) {
			continue;
		}

		if ( !Q_stricmp( trigger->classname, "trigger_push" ) ) {
			if ( ent->fly_sound_debounce_time < level.time ) {
				gentity_t	*te;

				ent->fly_sound_debounce_time = level.time + 1500;
				te = G_TempEntity( ent->r.currentOrigin, EV_GENERAL_SOUND );
				te->s.eventParm = G_SoundIndex( "sound/world/jumppad.wav" );
			}

			VectorCopy( ent->r.currentOrigin, ent->s.pos.trBase );
			VectorCopy( trigger->s.origin2, ent->s.pos.trDelta );
			ent->s.pos.trTime = level.previousTime;
			continue;
		}

		if ( !Q_stricmp( trigger->classname, "trigger_teleport" ) ) {
			gentity_t	*dest;
			gentity_t	*te;
			vec3_t		forward;

			dest = G_PickTarget( trigger->target );
			if ( !dest ) {
				G_Printf( "Couldn't find teleporter destination\n" );
				return;
			}

			te = G_TempEntity( ent->r.currentOrigin, EV_GENERAL_SOUND );
			te->s.eventParm = G_SoundIndex( "sound/world/teleout.ogg" );

			VectorCopy( dest->s.origin, ent->r.currentOrigin );
			VectorCopy( dest->s.origin, ent->s.pos.trBase );
			AngleVectors( dest->s.angles, forward, NULL, NULL );
			VectorScale( forward, 400, ent->s.pos.trDelta );
			ent->s.pos.trDelta[2] += 96;
			SnapVector( ent->s.pos.trDelta );
			ent->s.pos.trTime = level.previousTime;

			te = G_TempEntity( ent->r.currentOrigin, EV_GENERAL_SOUND );
			te->s.eventParm = G_SoundIndex( "sound/world/telein.ogg" );
		}

		if ( !Q_stricmp( trigger->classname, "trigger_capturezone" ) ) {
			G_DroppedPowerupTouchCaptureZone( trigger, ent );
		}
	}
}

/*
================
Touch_QuadHogItem

Announces the current Quad Hog carrier before falling back to the normal item pickup path.
================
*/
static void Touch_QuadHogItem( gentity_t *ent, gentity_t *other, trace_t *trace ) {
	if ( !other || !other->client ) {
		return;
	}

	trap_SendServerCommand( -1, va( "cp \"%s is the ^5Quad Hog!\"", other->client->pers.netname ) );
	Touch_Item( ent, other, trace );
}

/*
================
LaunchQuadHogItem

Spawns the retail Quad Hog world Quad entity with the custom touch announcer.
================
*/
static gentity_t *LaunchQuadHogItem( gitem_t *item, vec3_t origin, vec3_t velocity ) {
	gentity_t	*dropped;

	dropped = G_Spawn();

	dropped->s.eType = ET_ITEM;
	dropped->s.modelindex = item - bg_itemlist;
	dropped->s.modelindex2 = 1;
	dropped->classname = item->classname;
	dropped->item = item;
	VectorSet( dropped->r.mins, -ITEM_RADIUS, -ITEM_RADIUS, -ITEM_RADIUS );
	VectorSet( dropped->r.maxs, ITEM_RADIUS, ITEM_RADIUS, ITEM_RADIUS );
	dropped->r.contents = CONTENTS_TRIGGER;
	dropped->touch = Touch_QuadHogItem;
	G_SetOrigin( dropped, origin );
	dropped->s.pos.trType = TR_GRAVITY;
	dropped->s.pos.trTime = level.time;
	G_SetPowerupPOITime( dropped, level.time );
	G_SetItemRespawnTimerState( dropped, level.time, 0 );
	VectorCopy( velocity, dropped->s.pos.trDelta );
	dropped->s.eFlags |= EF_BOUNCE_HALF;
	dropped->physicsBounce = 0.50f;
	dropped->flags = FL_DROPPED_ITEM;
	dropped->think = G_FreeEntity;
	dropped->nextthink = level.time + 30000;
	trap_LinkEntity( dropped );

	return dropped;
}

/*
================
G_SpawnQuadHogQuad

Seeds the retail Quad Hog world Quad on a random deathmatch spawn.
================
*/
void G_SpawnQuadHogQuad( void ) {
	gentity_t	*spot;
	gentity_t	*countSpot;
	gitem_t		*item;
	int		choice;
	int		count;
	vec3_t		velocity;

	if ( !level.quadHogEnabled || g_gametype.integer != GT_FFA ) {
		return;
	}

	if ( level.intermissionQueued || level.intermissiontime ) {
		return;
	}

	item = BG_FindItemForPowerup( PW_QUAD );
	if ( !item ) {
		return;
	}

	RegisterItem( item );

	count = 0;
	countSpot = NULL;
	while ( ( countSpot = G_Find( countSpot, FOFS( classname ), "info_player_deathmatch" ) ) != NULL ) {
		count++;
	}

	spot = NULL;
	if ( count > 0 ) {
		choice = rand() % count;
		while ( choice-- >= 0 ) {
			spot = G_Find( spot, FOFS( classname ), "info_player_deathmatch" );
			if ( !spot ) {
				break;
			}
		}
	}

	if ( !spot ) {
		spot = G_Find( NULL, FOFS( classname ), "info_player_deathmatch" );
	}
	if ( !spot ) {
		return;
	}

	VectorClear( velocity );
	LaunchQuadHogItem( item, spot->s.origin, velocity );
	{
		gentity_t	*te;

		te = G_TempEntity( spot->s.origin, EV_GLOBAL_SOUND );
		te->s.eventParm = G_SoundIndex( "sound/items/poweruprespawn.wav" );
		te->r.svFlags |= SVF_BROADCAST;
	}
	trap_SendServerCommand( -1, "cp \"^5Quad ^7respawned!\"" );
}

/*
================
G_EnsureQuadHogQuad

Maintains the retail Quad Hog world Quad while no player is currently carrying Quad.
================
*/
void G_EnsureQuadHogQuad( void ) {
	gentity_t	*ent;
	int		i;

	if ( !level.quadHogEnabled || g_gametype.integer != GT_FFA ) {
		return;
	}

	for ( i = 0; i < level.maxclients; i++ ) {
		gentity_t	*player;

		player = &g_entities[i];
		if ( !player->inuse || !player->client ) {
			continue;
		}

		if ( player->client->ps.powerups[PW_QUAD] != 0 ) {
			return;
		}
	}

	ent = NULL;
	while ( ( ent = G_Find( ent, FOFS( classname ), "item_quad" ) ) != NULL ) {
		if ( !ent->inuse ) {
			continue;
		}
		if ( ent->r.contents == 0 || ( ent->s.eFlags & EF_NODRAW ) != 0 ) {
			continue;
		}

		return;
	}

	G_SpawnQuadHogQuad();
}

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

	if ( item && level.quadHogEnabled && g_gametype.integer == GT_FFA &&
		!Q_stricmp( item->classname, "item_quad" ) ) {
		return LaunchQuadHogItem( item, origin, velocity );
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
	if ( item->giType == IT_POWERUP ) {
		dropped->runFrame = G_DroppedPowerupRunFrame;
	}

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
	} else if ( item->giType == IT_PERSISTANT_POWERUP ) {
		dropped->think = G_RespawnItemPowerup;
		dropped->nextthink = level.time + 30000;
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
		if ( ent->client ) {
			ent->client->ps.stats[STAT_KEY_MASK] = ent->keyMask;
		}
		if ( ent->s.number >= 0 && ent->s.number < level.maxclients ) {
			G_BroadcastClientKeyMask( ent->s.number );
		}
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

		def = &defs[i];
		if ( !( ent->keyMask & def->bit ) ) {
			continue;
		}

		G_ResetKeyItem( def->bit );
	}

	ent->keyMask = 0;
	if ( ent->client ) {
		ent->client->ps.stats[STAT_KEY_MASK] = 0;
	}
	if ( ent->s.number >= 0 && ent->s.number < level.maxclients ) {
		G_BroadcastClientKeyMask( ent->s.number );
	}
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
	if ( !G_ItemFactorySpawnAllowed( ent->item ) ) {
		G_FreeEntity( ent );
		return;
	}

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
		int	respawn;

		respawn = g_spawnDelayPowerupSeconds;
		if ( respawn <= 0 ) {
			trap_LinkEntity (ent);
			return;
		}
		ent->s.eFlags |= EF_NODRAW;
		ent->r.contents = 0;
		ent->nextthink = level.time + respawn * 1000;
		ent->think = RespawnItem;
		G_SetPowerupPOITime( ent, ent->nextthink );
		G_SetItemRespawnTimerState( ent, ent->nextthink, respawn * 1000 );
		return;
	}

	if ( ent->item->giType == IT_KEY && g_spawnDelayKeySeconds > 0 ) {
		ent->s.eFlags |= EF_NODRAW;
		ent->r.contents = 0;
		ent->nextthink = level.time + g_spawnDelayKeySeconds * 1000;
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
	int	i;

	memset( itemRegistered, 0, sizeof( itemRegistered ) );

	// players always start with the base weapon
	RegisterItem( BG_FindItemForWeapon( WP_MACHINEGUN ) );
	RegisterItem( BG_FindItemForWeapon( WP_GAUNTLET ) );
	if( g_gametype.integer == GT_HARVESTER ) {
		RegisterItem( BG_FindItem( "Red Cube" ) );
		RegisterItem( BG_FindItem( "Blue Cube" ) );
	}

	if ( g_runes.integer ) {
		for ( i = 0; i < ARRAY_LEN( g_spawnItemPowerupTags ); i++ ) {
			RegisterItem( BG_FindItemForPowerup( g_spawnItemPowerupTags[i] ) );
		}
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
G_ItemRegistered

Returns whether the item has already been marked for level precache.
===============
*/
qboolean G_ItemRegistered( const gitem_t *item ) {
	int	itemIndex;

	if ( !item ) {
		return qfalse;
	}

	itemIndex = (int)( item - bg_itemlist );
	if ( itemIndex < 0 || itemIndex >= bg_numItems || itemIndex >= MAX_ITEMS ) {
		return qfalse;
	}

	return itemRegistered[itemIndex];
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

	if ( !G_ItemFactorySpawnAllowed( item ) ) {
		return;
	}

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

	// retail services per-frame item callbacks before deciding whether motion continues
	G_RunThink( ent );

	if ( ent->s.pos.trType == TR_STATIONARY ) {
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
