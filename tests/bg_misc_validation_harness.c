#include <string.h>

#include "q_shared.h"
#include "bg_public.h"

#if defined(_WIN32)
#define QLR_EXPORT __declspec(dllexport)
#else
#define QLR_EXPORT
#endif

/*
=============
Com_Printf

Test stub that discards bg_misc harness log output.
=============
*/
void Com_Printf( const char *fmt, ... ) {
	(void)fmt;
}

/*
=============
Com_Error

Test stub that keeps bg_misc harness calls from aborting the process.
=============
*/
void Com_Error( int level, const char *fmt, ... ) {
	(void)level;
	(void)fmt;
}

/*
=============
QLR_ItemModelIndex

Returns the bg_itemlist modelindex for one resolved item pointer.
=============
*/
static int QLR_ItemModelIndex( const gitem_t *item ) {
	if ( !item ) {
		return 0;
	}

	return (int)( item - bg_itemlist );
}

/*
=============
QLR_FindItemByClassnameChecked

Resolves one retail item definition for fixture setup.
=============
*/
static const gitem_t *QLR_FindItemByClassnameChecked( const char *classname ) {
	if ( !classname || !classname[0] ) {
		return NULL;
	}

	return BG_FindItemByClassname( classname );
}

/*
=============
QLR_ResetTrajectory

Seeds one stationary trajectory for deterministic pickup fixtures.
=============
*/
static void QLR_ResetTrajectory( trajectory_t *tr ) {
	memset( tr, 0, sizeof( *tr ) );
	tr->trType = TR_STATIONARY;
}

/*
=============
QLR_ResetPlayerState

Initialises a local playerState block with retail-neutral defaults.
=============
*/
static void QLR_ResetPlayerState( playerState_t *ps ) {
	memset( ps, 0, sizeof( *ps ) );
	ps->clientNum = 0;
	ps->persistant[PERS_TEAM] = TEAM_FREE;
	ps->stats[STAT_MAX_HEALTH] = 100;
}

/*
=============
QLR_ResetEntityItem

Initialises one stationary item entity for the requested item definition.
=============
*/
static void QLR_ResetEntityItem( entityState_t *ent, const gitem_t *item ) {
	memset( ent, 0, sizeof( *ent ) );
	ent->modelindex = QLR_ItemModelIndex( item );
	QLR_ResetTrajectory( &ent->pos );
}

/*
=============
QLR_GetPowerupItemClassname

Returns the resolved classname for one retail powerup lookup.
=============
*/
QLR_EXPORT const char *QLR_GetPowerupItemClassname( int powerup ) {
	gitem_t	*item;

	item = BG_FindItemForPowerup( (powerup_t)powerup );
	if ( !item ) {
		return NULL;
	}

	return item->classname;
}

/*
=============
QLR_PlayerTouchesItemByClassname

Evaluates the shared pickup bounds for one named item at fixed deltas.
=============
*/
QLR_EXPORT int QLR_PlayerTouchesItemByClassname( const char *classname, float xDelta, float yDelta, float zDelta ) {
	const gitem_t	*itemDef;
	playerState_t	ps;
	entityState_t	item;

	itemDef = QLR_FindItemByClassnameChecked( classname );
	if ( !itemDef ) {
		return 0;
	}

	QLR_ResetPlayerState( &ps );
	QLR_ResetEntityItem( &item, itemDef );

	ps.origin[0] = xDelta;
	ps.origin[1] = yDelta;
	ps.origin[2] = zDelta;

	return BG_PlayerTouchesItem( &ps, &item, 0 ) ? 1 : 0;
}

/*
=============
QLR_CanGrabDroppedSelfWeaponAfterDelay

Checks the retail dropped-self pickup grace window for one weapon item.
=============
*/
QLR_EXPORT int QLR_CanGrabDroppedSelfWeaponAfterDelay( int elapsedMs ) {
	const gitem_t	*itemDef;
	playerState_t	ps;
	entityState_t	item;

	itemDef = BG_FindItemForWeapon( WP_ROCKET_LAUNCHER );
	if ( !itemDef ) {
		return 0;
	}

	QLR_ResetPlayerState( &ps );
	QLR_ResetEntityItem( &item, itemDef );

	ps.clientNum = 3;
	item.modelindex2 = 1;
	item.otherEntityNum = ps.clientNum;
	item.time2 = 1000;

	return BG_CanItemBeGrabbed( GT_FFA, item.time2 + elapsedMs, &item, &ps ) ? 1 : 0;
}

/*
=============
QLR_CanGrabOwnedWeaponWithAmmo

Checks the retail weapon gate for a held weapon with a supplied ammo count.
=============
*/
QLR_EXPORT int QLR_CanGrabOwnedWeaponWithAmmo( int ammoCount ) {
	const gitem_t	*itemDef;
	playerState_t	ps;
	entityState_t	item;

	itemDef = BG_FindItemForWeapon( WP_ROCKET_LAUNCHER );
	if ( !itemDef ) {
		return 0;
	}

	QLR_ResetPlayerState( &ps );
	QLR_ResetEntityItem( &item, itemDef );

	ps.stats[STAT_WEAPONS] = ( 1 << WP_ROCKET_LAUNCHER );
	ps.ammo[WP_ROCKET_LAUNCHER] = ammoCount;

	return BG_CanItemBeGrabbed( GT_FFA, 0, &item, &ps ) ? 1 : 0;
}

/*
=============
QLR_CanGrabAmmoPack

Checks the shared ammo-pack path for one two-weapon loadout snapshot.
=============
*/
QLR_EXPORT int QLR_CanGrabAmmoPack( int machinegunOwned, int machinegunAmmo, int rocketOwned, int rocketAmmo ) {
	const gitem_t	*itemDef;
	playerState_t	ps;
	entityState_t	item;

	itemDef = QLR_FindItemByClassnameChecked( "ammo_pack" );
	if ( !itemDef ) {
		return 0;
	}

	QLR_ResetPlayerState( &ps );
	QLR_ResetEntityItem( &item, itemDef );

	if ( machinegunOwned ) {
		ps.stats[STAT_WEAPONS] |= ( 1 << WP_MACHINEGUN );
	}
	if ( rocketOwned ) {
		ps.stats[STAT_WEAPONS] |= ( 1 << WP_ROCKET_LAUNCHER );
	}

	ps.ammo[WP_MACHINEGUN] = machinegunAmmo;
	ps.ammo[WP_ROCKET_LAUNCHER] = rocketAmmo;

	return BG_CanItemBeGrabbed( GT_FFA, 0, &item, &ps ) ? 1 : 0;
}

/*
=============
QLR_CanGrabHealthItem

Checks one named health item's upper-bound gate at the supplied health value.
=============
*/
QLR_EXPORT int QLR_CanGrabHealthItem( const char *classname, int health ) {
	const gitem_t	*itemDef;
	playerState_t	ps;
	entityState_t	item;

	itemDef = QLR_FindItemByClassnameChecked( classname );
	if ( !itemDef ) {
		return 0;
	}

	QLR_ResetPlayerState( &ps );
	QLR_ResetEntityItem( &item, itemDef );
	ps.stats[STAT_HEALTH] = health;

	return BG_CanItemBeGrabbed( GT_FFA, 0, &item, &ps ) ? 1 : 0;
}

/*
=============
QLR_CanGrabCtfFlag

Checks the retail CTF team-item branch for one player/item/carry state.
=============
*/
QLR_EXPORT int QLR_CanGrabCtfFlag( int playerTeam, int carriedFlagPowerup, int itemPowerup, int dropped ) {
	gitem_t		*itemDef;
	playerState_t	ps;
	entityState_t	item;

	itemDef = BG_FindItemForPowerup( (powerup_t)itemPowerup );
	if ( !itemDef ) {
		return 0;
	}

	QLR_ResetPlayerState( &ps );
	QLR_ResetEntityItem( &item, itemDef );
	ps.persistant[PERS_TEAM] = playerTeam;

	if ( carriedFlagPowerup > PW_NONE && carriedFlagPowerup < PW_NUM_POWERUPS ) {
		ps.powerups[carriedFlagPowerup] = 1;
	}

	if ( dropped ) {
		item.modelindex2 = 1;
		item.otherEntityNum = ps.clientNum + 1;
	}

	return BG_CanItemBeGrabbed( GT_CTF, 0, &item, &ps ) ? 1 : 0;
}
