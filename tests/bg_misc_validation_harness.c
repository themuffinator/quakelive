#include <string.h>

#include "q_shared.h"
#include "bg_public.h"

#if defined(_WIN32)
#define QLR_EXPORT __declspec(dllexport)
#else
#define QLR_EXPORT
#endif

#ifdef QAGAME
vmCvar_t g_armorTiered;
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
QLR_PackEventSnapshot

Packs a small event snapshot for ctypes fixture assertions.
=============
*/
static int QLR_PackEventSnapshot( int eventSequence, int event, int eventParm, int extra ) {
	return ( ( eventSequence & 0xff ) << 24 )
		| ( ( event & 0x3ff ) << 12 )
		| ( ( eventParm & 0xff ) << 4 )
		| ( extra & 0xf );
}

/*
=============
QLR_GetWeaponName

Returns the shared retail display name for one weapon enum.
=============
*/
QLR_EXPORT const char *QLR_GetWeaponName( int weapon ) {
	return BG_WeaponName( (weapon_t)weapon );
}

/*
=============
QLR_ItemTagForWeapon

Exposes the local weapon enum to retail item-tag bridge.
=============
*/
QLR_EXPORT int QLR_ItemTagForWeapon( int weapon ) {
	return BG_ItemTagForWeapon( (weapon_t)weapon );
}

/*
=============
QLR_WeaponForItemTag

Exposes the retail item-tag to local weapon enum bridge.
=============
*/
QLR_EXPORT int QLR_WeaponForItemTag( int itemTag ) {
	return BG_WeaponForItemTag( itemTag );
}

/*
=============
QLR_ItemTagForHoldable

Exposes the local holdable enum to retail item-tag bridge.
=============
*/
QLR_EXPORT int QLR_ItemTagForHoldable( int holdable ) {
	return BG_ItemTagForHoldable( (holdable_t)holdable );
}

/*
=============
QLR_HoldableForItemTag

Exposes the retail item-tag to local holdable enum bridge.
=============
*/
QLR_EXPORT int QLR_HoldableForItemTag( int itemTag ) {
	return BG_HoldableForItemTag( itemTag );
}

/*
=============
QLR_GetWeaponMaxAmmo

Returns the shared max-ammo cap for one weapon enum.
=============
*/
QLR_EXPORT int QLR_GetWeaponMaxAmmo( int weapon ) {
	return BG_GetWeaponMaxAmmo( (weapon_t)weapon );
}

/*
=============
QLR_GetWeaponAmmoPackSize

Returns the shared ammo-pack pickup size for one weapon enum.
=============
*/
QLR_EXPORT int QLR_GetWeaponAmmoPackSize( int weapon ) {
	return BG_GetWeaponAmmoPackSize( (weapon_t)weapon );
}

/*
=============
QLR_GetWeaponAmmoPackMaxStack

Returns the shared ammo-pack stack cap for one weapon enum.
=============
*/
QLR_EXPORT int QLR_GetWeaponAmmoPackMaxStack( int weapon ) {
	return BG_GetWeaponAmmoPackMaxStack( (weapon_t)weapon );
}

/*
=============
QLR_GetWeaponStatsCount

Returns the number of recovered shared weapon-stat rows.
=============
*/
QLR_EXPORT int QLR_GetWeaponStatsCount( void ) {
	return bg_weaponStatsCount;
}

/*
=============
QLR_GetWeaponStatsFlags

Returns the handicap flags stored in one recovered weapon-stat row.
=============
*/
QLR_EXPORT int QLR_GetWeaponStatsFlags( int weapon ) {
	const bgWeaponStats_t	*stats;

	stats = BG_GetWeaponStats( (weapon_t)weapon );
	if ( !stats ) {
		return -1;
	}

	return stats->handicapFlags;
}

/*
=============
QLR_GetHandicapScalarPermille

Returns one weapon handicap scalar scaled to permille for stable ctypes checks.
=============
*/
QLR_EXPORT int QLR_GetHandicapScalarPermille( int type, int weapon ) {
	float	scalar;

	scalar = BG_GetHandicapScalar( (handicap_type_t)type, (weapon_t)weapon );
	return (int)( scalar * 1000.0f + 0.5f );
}

/*
=============
QLR_FindItemIndexByPickupName

Returns the retail item index found through the pickup-name lookup helper.
=============
*/
QLR_EXPORT int QLR_FindItemIndexByPickupName( const char *pickupName ) {
	return QLR_ItemModelIndex( BG_FindItem( pickupName ) );
}

/*
=============
QLR_FindItemIndexByClassname

Returns the retail item index found through the classname lookup helper.
=============
*/
QLR_EXPORT int QLR_FindItemIndexByClassname( const char *classname ) {
	return QLR_ItemModelIndex( BG_FindItemByClassname( classname ) );
}

/*
=============
QLR_FindItemIndexByTypeAndTag

Returns the retail item index found through the type/tag lookup helper.
=============
*/
QLR_EXPORT int QLR_FindItemIndexByTypeAndTag( int type, int tag ) {
	return QLR_ItemModelIndex( BG_FindItemByTypeAndTag( (itemType_t)type, tag ) );
}

/*
=============
QLR_PlayerHasPersistantPowerupByClassname

Checks the guarded persistent-powerup helper against one stored item index.
=============
*/
QLR_EXPORT int QLR_PlayerHasPersistantPowerupByClassname( const char *classname, int powerup ) {
	const gitem_t	*itemDef;
	playerState_t	ps;

	itemDef = QLR_FindItemByClassnameChecked( classname );

	QLR_ResetPlayerState( &ps );
	ps.stats[STAT_PERSISTANT_POWERUP] = QLR_ItemModelIndex( itemDef );

	return BG_PlayerHasPersistantPowerup( &ps, (powerup_t)powerup ) ? 1 : 0;
}

/*
=============
QLR_PlayerHasPersistantPowerupWithIndex

Checks out-of-range persistent-powerup indexes through the shared helper.
=============
*/
QLR_EXPORT int QLR_PlayerHasPersistantPowerupWithIndex( int itemIndex, int powerup ) {
	playerState_t	ps;

	QLR_ResetPlayerState( &ps );
	ps.stats[STAT_PERSISTANT_POWERUP] = itemIndex;

	return BG_PlayerHasPersistantPowerup( &ps, (powerup_t)powerup ) ? 1 : 0;
}

/*
=============
QLR_GetHealthArmorBoundsSnapshot

Packs armor and health upper-bound helper results for one player snapshot.
=============
*/
QLR_EXPORT int QLR_GetHealthArmorBoundsSnapshot( int maxHealth, int pickupQuantity ) {
	playerState_t	ps;
	int		armorBound;
	int		healthBound;

	QLR_ResetPlayerState( &ps );
	ps.stats[STAT_MAX_HEALTH] = maxHealth;

	armorBound = BG_GetArmorUpperBound( &ps );
	healthBound = BG_GetHealthUpperBound( &ps, pickupQuantity );

	return ( ( armorBound & 0xffff ) << 16 ) | ( healthBound & 0xffff );
}

/*
=============
QLR_ClearArmorTierIfEmpty

Returns the armor tier after running the shared strip/disable helper.
=============
*/
QLR_EXPORT int QLR_ClearArmorTierIfEmpty( int armor, int armorTier, int armorTiered ) {
	playerState_t	ps;

	QLR_ResetPlayerState( &ps );
	ps.stats[STAT_ARMOR] = armor;
	ps.armorTier = armorTier;

	BG_ClearArmorTierIfEmpty( &ps, armorTiered ? qtrue : qfalse );

	return ps.armorTier;
}

/*
=============
QLR_AddPredictableEventSnapshot

Queues one predictable event and returns the written slot snapshot.
=============
*/
QLR_EXPORT int QLR_AddPredictableEventSnapshot( int startSequence, int event, int eventParm ) {
	playerState_t	ps;
	int		slot;

	QLR_ResetPlayerState( &ps );
	ps.eventSequence = startSequence;

	BG_AddPredictableEventToPlayerstate( event, eventParm, &ps );

	slot = startSequence & ( MAX_PS_EVENTS - 1 );
	return QLR_PackEventSnapshot( ps.eventSequence, ps.events[slot], ps.eventParms[slot], slot );
}

/*
=============
QLR_TouchJumpPadSnapshot

Touches a synthetic jump pad and returns the event/cache snapshot.
=============
*/
QLR_EXPORT int QLR_TouchJumpPadSnapshot( int pmType, int flightPowerup, int previousJumppad ) {
	playerState_t	ps;
	entityState_t	jumppad;

	QLR_ResetPlayerState( &ps );
	memset( &jumppad, 0, sizeof( jumppad ) );

	ps.pm_type = (pmtype_t)pmType;
	ps.pmove_framecount = 42;
	ps.jumppad_ent = previousJumppad;
	if ( flightPowerup ) {
		ps.powerups[PW_FLIGHT] = 1;
	}

	jumppad.number = 7;
	jumppad.origin2[0] = 10.0f;
	jumppad.origin2[1] = 20.0f;
	jumppad.origin2[2] = 30.0f;

	BG_TouchJumpPad( &ps, &jumppad );

	return QLR_PackEventSnapshot( ps.eventSequence, ps.events[0], ps.eventParms[0], ps.jumppad_ent );
}

/*
=============
QLR_TouchJumpPadVelocityZ

Returns the resulting vertical velocity from the synthetic jump pad fixture.
=============
*/
QLR_EXPORT int QLR_TouchJumpPadVelocityZ( int pmType, int flightPowerup, int previousJumppad ) {
	playerState_t	ps;
	entityState_t	jumppad;

	QLR_ResetPlayerState( &ps );
	memset( &jumppad, 0, sizeof( jumppad ) );

	ps.pm_type = (pmtype_t)pmType;
	ps.jumppad_ent = previousJumppad;
	if ( flightPowerup ) {
		ps.powerups[PW_FLIGHT] = 1;
	}

	jumppad.number = 7;
	jumppad.origin2[2] = 30.0f;

	BG_TouchJumpPad( &ps, &jumppad );

	return (int)ps.velocity[2];
}

/*
=============
QLR_ShouldClearJumpPadLaunch

Returns the shared jump-pad launch clear decision for a synthetic playerstate.
=============
*/
QLR_EXPORT int QLR_ShouldClearJumpPadLaunch( int currentFrame, int jumpPadFrame, float velocityZ, int jumpPadEnt ) {
	playerState_t	ps;

	QLR_ResetPlayerState( &ps );
	ps.pm_type = PM_NORMAL;
	ps.pmove_framecount = currentFrame;
	ps.jumppad_frame = jumpPadFrame;
	ps.jumppad_ent = jumpPadEnt;
	ps.velocity[2] = velocityZ;

	return BG_ShouldClearJumpPadLaunch( &ps ) ? 1 : 0;
}

/*
=============
QLR_ProjectPredictableEventSnapshot

Projects one playerstate event into entityState event fields.
=============
*/
QLR_EXPORT int QLR_ProjectPredictableEventSnapshot( int entityEventSequence, int eventSequence ) {
	playerState_t	ps;
	entityState_t	ent;

	QLR_ResetPlayerState( &ps );
	memset( &ent, 0, sizeof( ent ) );

	ps.pm_type = PM_NORMAL;
	ps.stats[STAT_HEALTH] = 100;
	ps.entityEventSequence = entityEventSequence;
	ps.eventSequence = eventSequence;
	ps.events[0] = EV_JUMP;
	ps.eventParms[0] = 11;
	ps.events[1] = EV_FALL_FAR;
	ps.eventParms[1] = 22;

	BG_PlayerStateToEntityState( &ps, &ent, qfalse );

	return QLR_PackEventSnapshot( ps.entityEventSequence, ent.event, ent.eventParm, ent.eType );
}

/*
=============
QLR_ProjectExternalEventSnapshot

Projects an external playerstate event and confirms it takes event precedence.
=============
*/
QLR_EXPORT int QLR_ProjectExternalEventSnapshot( void ) {
	playerState_t	ps;
	entityState_t	ent;

	QLR_ResetPlayerState( &ps );
	memset( &ent, 0, sizeof( ent ) );

	ps.pm_type = PM_NORMAL;
	ps.stats[STAT_HEALTH] = 100;
	ps.externalEvent = EV_FALL_FAR;
	ps.externalEventParm = 55;
	ps.eventSequence = 1;
	ps.events[0] = EV_JUMP;
	ps.eventParms[0] = 11;

	BG_PlayerStateToEntityState( &ps, &ent, qfalse );

	return QLR_PackEventSnapshot( ps.entityEventSequence, ent.event, ent.eventParm, ent.eType );
}

/*
=============
QLR_ProjectPlayerStateVisibilitySnapshot

Packs eType, eFlags, number, and clientNum after playerstate projection.
=============
*/
QLR_EXPORT int QLR_ProjectPlayerStateVisibilitySnapshot( int pmType, int health, int eFlags ) {
	playerState_t	ps;
	entityState_t	ent;

	QLR_ResetPlayerState( &ps );
	memset( &ent, 0, sizeof( ent ) );

	ps.pm_type = (pmtype_t)pmType;
	ps.stats[STAT_HEALTH] = health;
	ps.eFlags = eFlags;
	ps.clientNum = 17;

	BG_PlayerStateToEntityState( &ps, &ent, qfalse );

	return ( ( ent.eType & 0xf ) << 28 )
		| ( ( ent.eFlags & 0xfff ) << 16 )
		| ( ( ent.number & 0xff ) << 8 )
		| ( ent.clientNum & 0xff );
}

/*
=============
QLR_ProjectPlayerStateReplicationSnapshotA

Packs the weapon, ground entity, loop sound, and generic payload projection.
=============
*/
QLR_EXPORT int QLR_ProjectPlayerStateReplicationSnapshotA( void ) {
	playerState_t	ps;
	entityState_t	ent;

	QLR_ResetPlayerState( &ps );
	memset( &ent, 0, sizeof( ent ) );

	ps.pm_type = PM_NORMAL;
	ps.stats[STAT_HEALTH] = 100;
	ps.weapon = WP_ROCKET_LAUNCHER;
	ps.groundEntityNum = 42;
	ps.loopSound = 7;
	ps.generic1 = 3;

	BG_PlayerStateToEntityState( &ps, &ent, qfalse );

	return ( ( ent.weapon & 0xff ) << 24 )
		| ( ( ent.groundEntityNum & 0xff ) << 16 )
		| ( ( ent.loopSound & 0xff ) << 8 )
		| ( ent.generic1 & 0xff );
}

/*
=============
QLR_ProjectPlayerStateReplicationSnapshotB

Packs animation and powerup-bit projection from playerstate to entitystate.
=============
*/
QLR_EXPORT int QLR_ProjectPlayerStateReplicationSnapshotB( void ) {
	playerState_t	ps;
	entityState_t	ent;

	QLR_ResetPlayerState( &ps );
	memset( &ent, 0, sizeof( ent ) );

	ps.pm_type = PM_NORMAL;
	ps.stats[STAT_HEALTH] = 100;
	ps.legsAnim = 21;
	ps.torsoAnim = 22;
	ps.powerups[PW_QUAD] = 1;
	ps.powerups[PW_FLIGHT] = 1;
	ps.powerups[PW_BLUEFLAG] = 1;

	BG_PlayerStateToEntityState( &ps, &ent, qfalse );

	return ( ( ent.legsAnim & 0xff ) << 24 )
		| ( ( ent.torsoAnim & 0xff ) << 16 )
		| ( ent.powerups & 0xffff );
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
QLR_CanGrabArmorItem

Checks one named armor item's classic or tiered pickup gate.
=============
*/
QLR_EXPORT int QLR_CanGrabArmorItem( const char *classname, int armor, int armorTier, int maxHealth, int armorTiered, int scoutPowerup ) {
	const gitem_t	*itemDef;
	const gitem_t	*scoutDef;
	playerState_t	ps;
	entityState_t	item;

	itemDef = QLR_FindItemByClassnameChecked( classname );
	if ( !itemDef ) {
		return 0;
	}

	QLR_ResetPlayerState( &ps );
	QLR_ResetEntityItem( &item, itemDef );

	ps.stats[STAT_ARMOR] = armor;
	ps.stats[STAT_MAX_HEALTH] = maxHealth;
	ps.armorTier = armorTier;

	if ( scoutPowerup ) {
		scoutDef = QLR_FindItemByClassnameChecked( "item_scout" );
		ps.stats[STAT_PERSISTANT_POWERUP] = QLR_ItemModelIndex( scoutDef );
	}

#ifdef QAGAME
	g_armorTiered.integer = armorTiered;
#else
	(void)armorTiered;
#endif

	return BG_CanItemBeGrabbed( GT_FFA, 0, &item, &ps ) ? 1 : 0;
}

/*
=============
QLR_ApplyArmorPickup

Applies one armor item and packs the resulting armor and tier for tests.
=============
*/
QLR_EXPORT int QLR_ApplyArmorPickup( const char *classname, int armor, int armorTier, int maxHealth, int armorTiered ) {
	const gitem_t	*itemDef;
	playerState_t	ps;

	itemDef = QLR_FindItemByClassnameChecked( classname );
	if ( !itemDef ) {
		return -1;
	}

	QLR_ResetPlayerState( &ps );
	ps.stats[STAT_ARMOR] = armor;
	ps.stats[STAT_MAX_HEALTH] = maxHealth;
	ps.armorTier = armorTier;

	BG_ApplyArmorPickup( &ps, itemDef, armorTiered ? qtrue : qfalse );

	return ( ps.stats[STAT_ARMOR] << 8 ) | ( ps.armorTier & 0xff );
}

/*
=============
QLR_UpdateArmorTier

Returns the armor tier rebuilt for one current armor value.
=============
*/
QLR_EXPORT int QLR_UpdateArmorTier( int armor, int armorTiered ) {
	playerState_t	ps;

	QLR_ResetPlayerState( &ps );
	ps.stats[STAT_ARMOR] = armor;
	ps.armorTier = 2;

	BG_UpdateArmorTierFromCurrentArmor( &ps, armorTiered ? qtrue : qfalse );

	return ps.armorTier;
}

/*
=============
QLR_GetArmorRegenTarget

Returns the shared armor-regen cap for one armor tier snapshot.
=============
*/
QLR_EXPORT int QLR_GetArmorRegenTarget( int maxHealth, int armorTier, int armorTiered ) {
	playerState_t	ps;

	QLR_ResetPlayerState( &ps );
	ps.stats[STAT_MAX_HEALTH] = maxHealth;
	ps.armorTier = armorTier;

	return BG_GetArmorRegenTarget( &ps, armorTiered ? qtrue : qfalse );
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
