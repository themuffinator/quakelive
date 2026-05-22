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
// bg_misc.c -- both games misc functions, all completely stateless

#include "q_shared.h"
#include "bg_public.h"

#ifdef CGAME
extern vmCvar_t cg_armorTiered;
#else
#ifdef QAGAME
extern vmCvar_t g_armorTiered;
#endif
#endif

const bgWeaponStats_t bg_weaponStats[] = {
	{ WP_GAUNTLET, 0, -1, 0, 0.000000000f, 0.847000003f, 1.000000000f, 1.000000000f },
	{ WP_MACHINEGUN, 50, 200, 0, 1.000000000f, 1.000000000f, 0.000000000f, 1.000000000f },
	{ WP_SHOTGUN, 10, 40, 1, 1.000000000f, 0.490000010f, 0.000000000f, 1.000000000f },
	{ WP_GRENADE_LAUNCHER, 5, 20, 0, 0.007000000f, 0.564000010f, 0.070000000f, 1.000000000f },
	{ WP_ROCKET_LAUNCHER, 5, 20, 1, 1.000000000f, 0.003000000f, 0.003000000f, 1.000000000f },
	{ WP_LIGHTNING, 60, 240, 1, 1.000000000f, 1.000000000f, 0.728999972f, 1.000000000f },
	{ WP_RAILGUN, 10, 40, 1, 0.000000000f, 1.000000000f, 0.000000000f, 1.000000000f },
	{ WP_PLASMAGUN, 30, 120, 1, 0.772000015f, 0.000000000f, 1.000000000f, 1.000000000f },
	{ WP_BFG, 15, 60, 0, 0.003000000f, 0.351999998f, 1.000000000f, 1.000000000f },
	{ WP_GRAPPLING_HOOK, 0, -1, 0, 0.317000002f, 0.666000009f, 0.861999989f, 1.000000000f },
	{ WP_NAILGUN, 20, 80, 0, 0.000000000f, 1.000000000f, 0.700999975f, 1.000000000f },
	{ WP_PROX_LAUNCHER, 10, 40, 0, 1.000000000f, 0.000000000f, 0.486000001f, 1.000000000f },
	{ WP_CHAINGUN, 100, 400, 0, 0.721000016f, 0.721000016f, 0.721000016f, 1.000000000f },
	{ WP_HEAVY_MACHINEGUN, 50, 200, 1, 0.806999981f, 0.647000015f, 0.000000000f, 1.000000000f }
};

const int bg_weaponStatsCount = sizeof( bg_weaponStats ) / sizeof( bg_weaponStats[0] );

static const int bg_weaponMaxAmmo[WP_NUM_WEAPONS] = {
	0,			// WP_NONE
	0,			// WP_GAUNTLET
	200,	// WP_MACHINEGUN
	200,	// WP_HEAVY_MACHINEGUN
	40,		// WP_SHOTGUN
	20,		// WP_GRENADE_LAUNCHER
	20,		// WP_ROCKET_LAUNCHER
	240,	// WP_LIGHTNING
	40,		// WP_RAILGUN
	120,	// WP_PLASMAGUN
	60,		// WP_BFG
	0,			// WP_GRAPPLING_HOOK
	80,		// WP_NAILGUN
	40,		// WP_PROX_LAUNCHER
	400		// WP_CHAINGUN
};

static const int bg_weaponToItemTag[WP_NUM_WEAPONS] = {
	0,
	ITEMTAG_WEAPON_GAUNTLET,
	ITEMTAG_WEAPON_MACHINEGUN,
	ITEMTAG_WEAPON_HEAVY_MACHINEGUN,
	ITEMTAG_WEAPON_SHOTGUN,
	ITEMTAG_WEAPON_GRENADE_LAUNCHER,
	ITEMTAG_WEAPON_ROCKET_LAUNCHER,
	ITEMTAG_WEAPON_LIGHTNING,
	ITEMTAG_WEAPON_RAILGUN,
	ITEMTAG_WEAPON_PLASMAGUN,
	ITEMTAG_WEAPON_BFG,
	ITEMTAG_WEAPON_GRAPPLING_HOOK,
	ITEMTAG_WEAPON_NAILGUN,
	ITEMTAG_WEAPON_PROX_LAUNCHER,
	ITEMTAG_WEAPON_CHAINGUN
};

static const weapon_t bg_itemTagToWeapon[WP_NUM_WEAPONS] = {
	WP_NONE,
	WP_GAUNTLET,
	WP_MACHINEGUN,
	WP_SHOTGUN,
	WP_GRENADE_LAUNCHER,
	WP_ROCKET_LAUNCHER,
	WP_LIGHTNING,
	WP_RAILGUN,
	WP_PLASMAGUN,
	WP_BFG,
	WP_GRAPPLING_HOOK,
	WP_NAILGUN,
	WP_PROX_LAUNCHER,
	WP_CHAINGUN,
	WP_HEAVY_MACHINEGUN
};

static const int bg_holdableToItemTag[HI_NUM_HOLDABLE] = {
	0,
	ITEMTAG_HOLDABLE_TELEPORTER,
	ITEMTAG_HOLDABLE_MEDKIT,
	ITEMTAG_HOLDABLE_KAMIKAZE,
	ITEMTAG_HOLDABLE_PORTAL,
	ITEMTAG_HOLDABLE_INVULNERABILITY
};

static const holdable_t bg_itemTagToHoldable[ITEMTAG_HOLDABLE_INVULNERABILITY + 1] = {
	HI_NONE,
	HI_TELEPORTER,
	HI_MEDKIT,
	HI_KAMIKAZE,
	HI_PORTAL,
	HI_NONE,
	HI_INVULNERABILITY
};

static const char *const bg_retailWeaponNames[WP_NUM_WEAPONS] = {
	[WP_NONE] = "None",
	[ITEMTAG_WEAPON_GAUNTLET] = "Gauntlet",
	[ITEMTAG_WEAPON_MACHINEGUN] = "Machine Gun",
	[ITEMTAG_WEAPON_SHOTGUN] = "Shotgun",
	[ITEMTAG_WEAPON_GRENADE_LAUNCHER] = "Grenade Launcher",
	[ITEMTAG_WEAPON_ROCKET_LAUNCHER] = "Rocket Launcher",
	[ITEMTAG_WEAPON_LIGHTNING] = "Lightning Gun",
	[ITEMTAG_WEAPON_RAILGUN] = "Railgun",
	[ITEMTAG_WEAPON_PLASMAGUN] = "Plasma Gun",
	[ITEMTAG_WEAPON_BFG] = "BFG10K",
	[ITEMTAG_WEAPON_GRAPPLING_HOOK] = "Grappling Hook",
	[ITEMTAG_WEAPON_NAILGUN] = "Nailgun",
	[ITEMTAG_WEAPON_PROX_LAUNCHER] = "Prox Launcher",
	[ITEMTAG_WEAPON_CHAINGUN] = "Chaingun",
	[ITEMTAG_WEAPON_HEAVY_MACHINEGUN] = "Heavy Machinegun"
};

/*
=============
BG_GetWeaponStats

Returns the stat record for a weapon enumeration or NULL when no mapping exists.
=============
*/
const bgWeaponStats_t *BG_GetWeaponStats( weapon_t weapon ) {
	int		index;

	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return NULL;
	}

	for ( index = 0; index < bg_weaponStatsCount; index++ ) {
		if ( bg_weaponStats[index].weapon == weapon ) {
			return &bg_weaponStats[index];
		}
	}

	return NULL;
}

/*
=============
BG_GetWeaponMaxAmmo

Returns the hard cap for the supplied weapon type. Dropped ammo ignores the
limit so players can still recover after a weapon toss.
=============
*/
int BG_GetWeaponMaxAmmo( weapon_t weapon ) {
	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return 0;
	}

	return bg_weaponMaxAmmo[weapon];
}

/*
=============
BG_ItemTagForWeapon

Returns the retail bg_itemlist weapon/ammo tag for the supplied weapon enum.
=============
*/
int BG_ItemTagForWeapon( weapon_t weapon ) {
	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		if ( weapon == WP_NUM_WEAPONS ) {
			return WP_NUM_WEAPONS;
		}
		return WP_NONE;
	}

	return bg_weaponToItemTag[weapon];
}

/*
=============
BG_WeaponForItemTag

Maps a retail bg_itemlist weapon/ammo tag back to the local weapon enum.
=============
*/
weapon_t BG_WeaponForItemTag( int itemTag ) {
	if ( itemTag == WP_NUM_WEAPONS ) {
		return WP_NUM_WEAPONS;
	}

	if ( itemTag <= WP_NONE || itemTag >= WP_NUM_WEAPONS ) {
		return WP_NONE;
	}

	return bg_itemTagToWeapon[itemTag];
}

/*
=============
BG_ItemTagForHoldable

Returns the retail bg_itemlist holdable tag for the supplied holdable enum.
=============
*/
int BG_ItemTagForHoldable( holdable_t holdable ) {
	if ( holdable <= HI_NONE || holdable >= HI_NUM_HOLDABLE ) {
		return HI_NONE;
	}

	return bg_holdableToItemTag[holdable];
}

/*
=============
BG_HoldableForItemTag

Maps a retail bg_itemlist holdable tag back to the local holdable enum.
=============
*/
holdable_t BG_HoldableForItemTag( int itemTag ) {
	if ( itemTag <= HI_NONE || itemTag > ITEMTAG_HOLDABLE_INVULNERABILITY ) {
		return HI_NONE;
	}

	return bg_itemTagToHoldable[itemTag];
}

/*
=============
BG_GetHandicapScalar

Returns the handicap scalar associated with the requested weapon and type.
=============
*/
float BG_GetHandicapScalar( handicap_type_t type, weapon_t weapon ) {
	const bgWeaponStats_t	*stats;

	if ( type < 0 || type >= HANDICAP_SCALAR_MAX ) {
		return 1.0f;
	}

	stats = BG_GetWeaponStats( weapon );
	if ( !stats ) {
		return 1.0f;
	}

	switch ( type ) {
	case HANDICAP_SCALAR_PICKUP:
		return stats->pickupHandicapScale;
	case HANDICAP_SCALAR_ARMOR:
		return stats->armorHandicapScale;
	case HANDICAP_SCALAR_HEALTH:
		return stats->healthHandicapScale;
	case HANDICAP_SCALAR_RESPAWN:
		return stats->respawnHandicapScale;
	default:
		break;
	}

	return 1.0f;
}

/*
=============
BG_GetWeaponAmmoPackSize

Returns the default ammo pack pickup size for the supplied weapon.
=============
*/
int BG_GetWeaponAmmoPackSize( weapon_t weapon ) {
	const bgWeaponStats_t	*stats;

	stats = BG_GetWeaponStats( weapon );
	if ( !stats ) {
		return 0;
	}

	return stats->pickupQuantity;
}

/*
=============
BG_GetWeaponAmmoPackMaxStack

Returns the standard ammo stack cap for the supplied weapon.
=============
*/
int BG_GetWeaponAmmoPackMaxStack( weapon_t weapon ) {
	const bgWeaponStats_t	*stats;

	stats = BG_GetWeaponStats( weapon );
	if ( !stats ) {
		return 0;
	}

	return stats->maxStack;
}

/*
=============
BG_PlayerHasPersistantPowerup

Returns whether the persistant powerup stored in the supplied playerstate
matches the requested tag.
=============
*/
qboolean BG_PlayerHasPersistantPowerup( const playerState_t *ps, powerup_t powerup ) {
	const gitem_t	*item;

	if ( !ps ) {
		return qfalse;
	}

	if ( powerup <= PW_NONE || powerup >= PW_NUM_POWERUPS ) {
		return qfalse;
	}

	if ( ps->stats[STAT_PERSISTANT_POWERUP] <= 0 || ps->stats[STAT_PERSISTANT_POWERUP] >= bg_numItems ) {
		return qfalse;
	}

	item = &bg_itemlist[ps->stats[STAT_PERSISTANT_POWERUP]];
	return (item->giTag == powerup) ? qtrue : qfalse;
}

/*
=============
BG_GetArmorUpperBound

Returns the maximum armor stack allowed for the supplied playerstate.
=============
*/
int BG_GetArmorUpperBound( const playerState_t *ps ) {
	if ( !ps ) {
		return 0;
	}

	return ps->stats[STAT_MAX_HEALTH] * 2;
}

/*
=============
BG_GetHealthUpperBound

Returns the maximum health stack allowed for a health pickup with the supplied
quantity.
=============
*/
int BG_GetHealthUpperBound( const playerState_t *ps, int pickupQuantity ) {
	int	upperBound;

	if ( !ps ) {
		return 0;
	}

	upperBound = ps->stats[STAT_MAX_HEALTH];
	if ( pickupQuantity == 5 || pickupQuantity == 100 ) {
		upperBound = ps->stats[STAT_MAX_HEALTH] * 2;
	}

	return upperBound;
}

/*
=============
BG_UpdateArmorTierFromCurrentArmor

Rebuilds the replicated retail armor tier from the current armor amount.
=============
*/
void BG_UpdateArmorTierFromCurrentArmor( playerState_t *ps, qboolean armorTiered ) {
	if ( !ps || !armorTiered || ps->stats[STAT_ARMOR] <= 0 ) {
		if ( ps ) {
			ps->armorTier = 0;
		}
		return;
	}

	if ( ps->stats[STAT_ARMOR] < 100 ) {
		ps->armorTier = 0;
	} else if ( ps->stats[STAT_ARMOR] < 150 ) {
		ps->armorTier = 1;
	} else {
		ps->armorTier = 2;
	}
}

/*
=============
BG_ClearArmorTierIfEmpty

Retail resets the armor tier once the player is fully stripped of armor.
=============
*/
void BG_ClearArmorTierIfEmpty( playerState_t *ps, qboolean armorTiered ) {
	if ( !ps ) {
		return;
	}

	if ( !armorTiered || ps->stats[STAT_ARMOR] < 1 ) {
		ps->armorTier = 0;
	}
}

/*
=============
BG_GetArmorRegenTarget

Returns the retail armor-regen cap for the current armor tier.
=============
*/
int BG_GetArmorRegenTarget( const playerState_t *ps, qboolean armorTiered ) {
	if ( !ps ) {
		return 0;
	}

	if ( !armorTiered ) {
		return ps->stats[STAT_MAX_HEALTH];
	}

	switch ( ps->armorTier ) {
	case 2:
		return 150;
	case 1:
		return 100;
	default:
		return 50;
	}
}

/*
=============
BG_ApplyArmorPickup

Applies retail Quake Live armor pickup semantics, including tiered armor.
=============
*/
void BG_ApplyArmorPickup( playerState_t *ps, const gitem_t *item, qboolean armorTiered ) {
	int	upperBound;

	if ( !ps || !item ) {
		return;
	}

	if ( !armorTiered ) {
		ps->stats[STAT_ARMOR] += item->quantity;
		upperBound = BG_GetArmorUpperBound( ps );
		if ( upperBound > 0 && ps->stats[STAT_ARMOR] > upperBound ) {
			ps->stats[STAT_ARMOR] = upperBound;
		}
		return;
	}

	switch ( item->giTag ) {
	case 1:
		ps->stats[STAT_ARMOR] += 150;
		if ( ps->stats[STAT_ARMOR] > 200 ) {
			ps->stats[STAT_ARMOR] = 200;
		}
		ps->armorTier = 2;
		break;
	case 2:
		ps->stats[STAT_ARMOR] += 100;
		if ( ps->stats[STAT_ARMOR] > 150 ) {
			ps->stats[STAT_ARMOR] = 150;
		}
		ps->armorTier = 1;
		break;
	case 3:
		ps->stats[STAT_ARMOR] += 50;
		if ( ps->stats[STAT_ARMOR] > 100 ) {
			ps->stats[STAT_ARMOR] = 100;
		}
		ps->armorTier = 0;
		break;
	default:
		if ( ps->stats[STAT_ARMOR] < 1 ) {
			ps->armorTier = 0;
		}
		ps->stats[STAT_ARMOR] += 2;
		break;
	}

	upperBound = BG_GetArmorUpperBound( ps );
	if ( upperBound > 0 && ps->stats[STAT_ARMOR] > upperBound ) {
		ps->stats[STAT_ARMOR] = upperBound;
	}
}

/*QUAKED item_***** ( 0 0 0 ) (-16 -16 -16) (16 16 16) suspended
DO NOT USE THIS CLASS, IT JUST HOLDS GENERAL INFORMATION.
The suspended flag will allow items to hang in the air, otherwise they are dropped to the next surface.

If an item is the target of another entity, it will not spawn in until fired.

An item fires all of its targets when it is picked up.  If the toucher can't carry it, the targets won't be fired.

"notfree" if set to 1, don't spawn in free for all games
"notteam" if set to 1, don't spawn in team games
"notsingle" if set to 1, don't spawn in single player games
"wait"	override the default wait before respawning.  -1 = never respawn automatically, which can be used with targeted spawning.
"random" random number of plus or minus seconds varied from the respawn time
"count" override quantity or duration on most items.
*/

gitem_t	bg_itemlist[] = 
{
	{
		NULL,
		NULL,
		{ NULL,
		NULL,
		0, 0} ,
/* icon */		NULL,
/* pickup */	NULL,
		0,
		0,
		0,
/* precache */ "",
/* sounds */ ""
	},	// leave index 0 alone

	//
	// ARMOR
	//

/*QUAKED item_armor_shard (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_armor_shard", 
		"sound/misc/ar1_pkup.wav",
		{ "models/powerups/armor/shard.md3", 
		"models/powerups/armor/shard_sphere.md3",
		0, 0} ,
/* icon */		"icons/iconr_shard",
/* pickup */	"Armor Shard",
		5,
		IT_ARMOR,
		4,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED item_armor_combat (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_armor_combat", 
		"sound/misc/ar2_pkup.wav",
        { "models/powerups/armor/armor_yel.md3",
		0, 0, 0},
/* icon */		"icons/iconr_yellow",
/* pickup */	"Yellow Armor",
		50,
		IT_ARMOR,
		2,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED item_armor_body (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_armor_body", 
		"sound/misc/ar2_pkup.wav",
        { "models/powerups/armor/armor_red.md3",
		0, 0, 0},
/* icon */		"icons/iconr_red",
/* pickup */	"Red Armor",
		100,
		IT_ARMOR,
		1,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED item_armor_jacket (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_armor_jacket",
		"sound/misc/ar2_pkup.wav",
	{ "models/powerups/armor/armor_grn.md3",
		0, 0, 0},
/* icon */		"icons/iconr_green",
/* pickup */	"Green Armor",
		25,
		IT_ARMOR,
		3,
/* precache */	"",
/* sounds */	""
	},

	//
	// health
	//
/*QUAKED item_health_small (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_health_small",
		"sound/items/s_health.wav",
        { "models/powerups/health/small_cross.md3", 
		"models/powerups/health/small_sphere.md3", 
		0, 0 },
/* icon */		"icons/iconh_green",
/* pickup */	"5 Health",
		5,
		IT_HEALTH,
		4,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED item_health (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_health",
		"sound/items/n_health.wav",
        { "models/powerups/health/medium_cross.md3", 
		"models/powerups/health/medium_sphere.md3", 
		0, 0 },
/* icon */		"icons/iconh_yellow",
/* pickup */	"25 Health",
		25,
		IT_HEALTH,
		3,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED item_health_large (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_health_large",
		"sound/items/l_health.wav",
        { "models/powerups/health/large_cross.md3", 
		"models/powerups/health/large_sphere.md3", 
		0, 0 },
/* icon */		"icons/iconh_red",
/* pickup */	"50 Health",
		50,
		IT_HEALTH,
		2,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED item_health_mega (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_health_mega",
		"sound/items/m_health.wav",
        { "models/powerups/health/mega_cross.md3", 
		"models/powerups/health/mega_sphere.md3", 
		0, 0 },
/* icon */		"icons/iconh_mega",
/* pickup */	"Mega Health",
		100,
		IT_HEALTH,
		1,
/* precache */ "",
/* sounds */ ""
	},


	//
	// WEAPONS 
	//

/*QUAKED weapon_gauntlet (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_gauntlet", 
		"sound/misc/w_pkup.wav",
        { "models/weapons2/gauntlet/gauntlet.md3",
		0, 0, 0},
/* icon */		"icons/iconw_gauntlet",
/* pickup */	"Gauntlet",
		0,
		IT_WEAPON,
		ITEMTAG_WEAPON_GAUNTLET,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED weapon_shotgun (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_shotgun", 
		"sound/misc/w_pkup.wav",
        { "models/weapons2/shotgun/shotgun.md3", 
		0, 0, 0},
/* icon */		"icons/iconw_shotgun",
/* pickup */	"Shotgun",
		10,
		IT_WEAPON,
		ITEMTAG_WEAPON_SHOTGUN,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED weapon_machinegun (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_machinegun", 
		"sound/misc/w_pkup.wav",
        { "models/weapons2/machinegun/machinegun.md3", 
		0, 0, 0},
/* icon */		"icons/iconw_machinegun",
/* pickup */	"Machine Gun",
		100,
		IT_WEAPON,
		ITEMTAG_WEAPON_MACHINEGUN,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED weapon_grenadelauncher (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_grenadelauncher",
		"sound/misc/w_pkup.wav",
        { "models/weapons2/grenadel/grenadel.md3", 
		0, 0, 0},
/* icon */		"icons/iconw_grenade",
/* pickup */	"Grenade Launcher",
		10,
		IT_WEAPON,
		ITEMTAG_WEAPON_GRENADE_LAUNCHER,
/* precache */ "",
/* sounds */ "sound/weapons/grenade/hgrenb1a.wav sound/weapons/grenade/hgrenb2a.wav"
	},

/*QUAKED weapon_rocketlauncher (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_rocketlauncher",
		"sound/misc/w_pkup.wav",
        { "models/weapons2/rocketl/rocketl.md3", 
		0, 0, 0},
/* icon */		"icons/iconw_rocket",
/* pickup */	"Rocket Launcher",
		10,
		IT_WEAPON,
		ITEMTAG_WEAPON_ROCKET_LAUNCHER,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED weapon_lightning (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_lightning", 
		"sound/misc/w_pkup.wav",
        { "models/weapons2/lightning/lightning.md3", 
		0, 0, 0},
/* icon */		"icons/iconw_lightning",
/* pickup */	"Lightning Gun",
		100,
		IT_WEAPON,
		ITEMTAG_WEAPON_LIGHTNING,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED weapon_railgun (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_railgun", 
		"sound/misc/w_pkup.wav",
        { "models/weapons2/railgun/railgun.md3", 
		0, 0, 0},
/* icon */		"icons/iconw_railgun",
/* pickup */	"Railgun",
		10,
		IT_WEAPON,
		ITEMTAG_WEAPON_RAILGUN,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED weapon_plasmagun (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_plasmagun", 
		"sound/misc/w_pkup.wav",
        { "models/weapons2/plasma/plasma.md3", 
		0, 0, 0},
/* icon */		"icons/iconw_plasma",
/* pickup */	"Plasma Gun",
		50,
		IT_WEAPON,
		ITEMTAG_WEAPON_PLASMAGUN,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED weapon_bfg (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_bfg",
		"sound/misc/w_pkup.wav",
        { "models/weapons2/bfg/bfg.md3", 
		0, 0, 0},
/* icon */		"icons/iconw_bfg",
/* pickup */	"BFG10K",
		10,
		IT_WEAPON,
		ITEMTAG_WEAPON_BFG,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED weapon_grapplinghook (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_grapplinghook",
		"sound/misc/w_pkup.wav",
        { "models/weapons2/grapple/grapple.md3", 
		0, 0, 0},
/* icon */		"icons/iconw_grapple",
/* pickup */	"Grappling Hook",
		0,
		IT_WEAPON,
		ITEMTAG_WEAPON_GRAPPLING_HOOK,
/* precache */ "",
/* sounds */ ""
	},

	//
	// AMMO ITEMS
	//

/*QUAKED ammo_shells (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"ammo_shells",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/shotgunam.md3", 
		0, 0, 0},
/* icon */		"icons/icona_shotgun",
/* pickup */	"Shells",
		5,
		IT_AMMO,
		ITEMTAG_WEAPON_SHOTGUN,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED ammo_bullets (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"ammo_bullets",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/machinegunam.md3", 
		0, 0, 0},
/* icon */		"icons/icona_machinegun",
/* pickup */	"Bullets",
		50,
		IT_AMMO,
		ITEMTAG_WEAPON_MACHINEGUN,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED ammo_grenades (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"ammo_grenades",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/grenadeam.md3", 
		0, 0, 0},
/* icon */		"icons/icona_grenade",
/* pickup */	"Grenades",
		5,
		IT_AMMO,
		ITEMTAG_WEAPON_GRENADE_LAUNCHER,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED ammo_cells (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"ammo_cells",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/plasmaam.md3", 
		0, 0, 0},
/* icon */		"icons/icona_plasma",
/* pickup */	"Cells",
		50,
		IT_AMMO,
		ITEMTAG_WEAPON_PLASMAGUN,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED ammo_lightning (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"ammo_lightning",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/lightningam.md3", 
		0, 0, 0},
/* icon */		"icons/icona_lightning",
/* pickup */	"Lightning",
		50,
		IT_AMMO,
		ITEMTAG_WEAPON_LIGHTNING,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED ammo_rockets (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"ammo_rockets",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/rocketam.md3", 
		0, 0, 0},
/* icon */		"icons/icona_rocket",
/* pickup */	"Rockets",
		5,
		IT_AMMO,
		ITEMTAG_WEAPON_ROCKET_LAUNCHER,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED ammo_slugs (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"ammo_slugs",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/railgunam.md3", 
		0, 0, 0},
/* icon */		"icons/icona_railgun",
/* pickup */	"Slugs",
		5,
		IT_AMMO,
		ITEMTAG_WEAPON_RAILGUN,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED ammo_bfg (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"ammo_bfg",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/bfgam.md3", 
		0, 0, 0},
/* icon */		"icons/icona_bfg",
/* pickup */	"BFG Ammo",
		5,
		IT_AMMO,
		ITEMTAG_WEAPON_BFG,
/* precache */ "",
/* sounds */ ""
	},

	//
	// HOLDABLE ITEMS
	//
/*QUAKED holdable_teleporter (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"holdable_teleporter", 
		"sound/items/holdable.wav",
        { "models/powerups/holdable/teleporter.md3", 
		0, 0, 0},
/* icon */		"icons/teleporter",
/* pickup */	"Personal Teleporter",
		60,
		IT_HOLDABLE,
		ITEMTAG_HOLDABLE_TELEPORTER,
/* precache */ "",
/* sounds */ ""
	},
/*QUAKED holdable_medkit (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"holdable_medkit", 
		"sound/items/holdable.wav",
        { 
		"models/powerups/holdable/medkit.md3", 
		"models/powerups/holdable/medkit_sphere.md3",
		0, 0},
/* icon */		"icons/medkit",
/* pickup */	"Medkit",
		60,
		IT_HOLDABLE,
		ITEMTAG_HOLDABLE_MEDKIT,
/* precache */ "",
/* sounds */ "sound/items/use_medkit.wav"
	},


	//
	// POWERUP ITEMS
	//
/*QUAKED item_quad (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_quad", 
		"sound/items/damage3.ogg",
        { "models/powerups/instant/quad.md3", 
        "models/powerups/instant/quad_ring.md3",
		0, 0 },
/* icon */		"icons/quad",
/* pickup */	"Quad Damage",
		30,
		IT_POWERUP,
		PW_QUAD,
/* precache */ "",
/* sounds */ "sound/items/damage2.wav sound/items/damage3.wav"
	},

/*QUAKED item_enviro (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_enviro",
		"sound/items/protect.wav",
        { "models/powerups/instant/enviro.md3", 
		"models/powerups/instant/enviro_ring.md3", 
		0, 0 },
/* icon */		"icons/envirosuit",
/* pickup */	"Battle Suit",
		30,
		IT_POWERUP,
		PW_BATTLESUIT,
/* precache */ "",
/* sounds */ "sound/items/airout.wav sound/items/protect3.wav"
	},

/*QUAKED item_haste (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_haste",
		"sound/items/guard.wav",
        { "models/powerups/instant/haste.md3", 
		"models/powerups/instant/haste_ring.md3", 
		0, 0 },
/* icon */		"icons/haste",
/* pickup */	"Haste",
		30,
		IT_POWERUP,
		PW_HASTE,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED item_invis (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_invis",
		"sound/items/holdable.wav",
        { "models/powerups/instant/invis.md3", 
		"models/powerups/instant/invis_ring.md3", 
		0, 0 },
/* icon */		"icons/invis",
/* pickup */	"Invisibility",
		30,
		IT_POWERUP,
		PW_INVIS,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED item_regen (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_regen",
		"sound/items/holdable.wav",
        { "models/powerups/instant/regen.md3", 
		"models/powerups/instant/regen_ring.md3", 
		0, 0 },
/* icon */		"icons/regen",
/* pickup */	"Regeneration",
		30,
		IT_POWERUP,
		PW_REGEN,
/* precache */ "",
/* sounds */ "sound/items/regen.wav"
	},

/*QUAKED item_flight (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_flight",
		"sound/items/flight.wav",
        { "models/powerups/instant/flight.md3", 
		"models/powerups/instant/flight_ring.md3", 
		0, 0 },
/* icon */		"icons/flight",
/* pickup */	"Flight",
		60,
		IT_POWERUP,
		PW_FLIGHT,
/* precache */ "",
/* sounds */ "sound/items/flight.wav"
	},

/*QUAKED team_CTF_redflag (1 0 0) (-16 -16 -16) (16 16 16)
Only in CTF games
*/
	{
		"team_CTF_redflag",
		NULL,
        { "models/flags/r_flag.md3",
		0, "models/flag3/r_flag3.md3", 0 },
/* icon */		"gfx/2d/flag_status/red_flag_at_base",
/* pickup */	"Red Flag",
		0,
		IT_TEAM,
		PW_REDFLAG,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED team_CTF_blueflag (0 0 1) (-16 -16 -16) (16 16 16)
Only in CTF games
*/
	{
		"team_CTF_blueflag",
		NULL,
        { "models/flags/b_flag.md3",
		0, "models/flag3/b_flag3.md3", 0 },
/* icon */		"gfx/2d/flag_status/blue_flag_at_base",
/* pickup */	"Blue Flag",
		0,
		IT_TEAM,
		PW_BLUEFLAG,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED holdable_kamikaze (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"holdable_kamikaze", 
		"sound/items/holdable.wav",
        { "models/powerups/kamikazi.md3", 
		0, 0, 0},
/* icon */		"icons/kamikaze",
/* pickup */	"Kamikaze",
		60,
		IT_HOLDABLE,
		ITEMTAG_HOLDABLE_KAMIKAZE,
/* precache */ "",
/* sounds */ "sound/items/kamikazerespawn.wav"
	},

/*QUAKED holdable_portal (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"holdable_portal", 
		"sound/items/holdable.wav",
        { "models/powerups/holdable/porter.md3",
		0, 0, 0},
/* icon */		"icons/portal",
/* pickup */	"Portal",
		60,
		IT_HOLDABLE,
		ITEMTAG_HOLDABLE_PORTAL,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED holdable_invulnerability (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"holdable_invulnerability", 
		"sound/items/holdable.wav",
        { "models/powerups/holdable/invulnerability.md3", 
		0, 0, 0},
/* icon */		"icons/invulnerability",
/* pickup */	"Invulnerability",
		60,
		IT_HOLDABLE,
		ITEMTAG_HOLDABLE_INVULNERABILITY,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED ammo_nails (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"ammo_nails",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/nailgunam.md3", 
		0, 0, 0},
/* icon */		"icons/icona_nailgun",
/* pickup */	"Nails",
		5,
		IT_AMMO,
		ITEMTAG_WEAPON_NAILGUN,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED ammo_mines (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"ammo_mines",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/proxmineam.md3", 
		0, 0, 0},
/* icon */		"icons/icona_proxlauncher",
/* pickup */	"Proximity Mines",
		5,
		IT_AMMO,
		ITEMTAG_WEAPON_PROX_LAUNCHER,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED ammo_belt (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"ammo_belt",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/chaingunam.md3", 
		0, 0, 0},
/* icon */		"icons/icona_chaingun",
/* pickup */	"Chaingun Belt",
		100,
		IT_AMMO,
		ITEMTAG_WEAPON_CHAINGUN,
/* precache */ "",
/* sounds */ ""
	},

	//
	// PERSISTANT POWERUP ITEMS
	//
/*QUAKED item_scout (.3 .3 1) (-16 -16 -16) (16 16 16) suspended redTeam blueTeam
*/
	{
		"item_scout",
		"sound/items/scout.ogg",
        { "models/powerups/scout.md3", 
		0, 0, 0 },
/* icon */		"icons/scout",
/* pickup */	"Scout",
		0,
		IT_PERSISTANT_POWERUP,
		PW_SCOUT,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED item_guard (.3 .3 1) (-16 -16 -16) (16 16 16) suspended redTeam blueTeam
*/
	{
		"item_guard",
		"sound/items/guard.ogg",
        { "models/powerups/guard.md3", 
		0, 0, 0 },
/* icon */		"icons/guard",
/* pickup */	"Guard",
		0,
		IT_PERSISTANT_POWERUP,
		PW_GUARD,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED item_doubler (.3 .3 1) (-16 -16 -16) (16 16 16) suspended redTeam blueTeam
*/
	{
		"item_doubler",
		"sound/items/damage.ogg",
        { "models/powerups/doubler.md3", 
		0, 0, 0 },
/* icon */		"icons/doubler",
/* pickup */	"Damage",
		0,
		IT_PERSISTANT_POWERUP,
		PW_DOUBLER,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED item_armorregen (.3 .3 1) (-16 -16 -16) (16 16 16) suspended redTeam blueTeam
*/
	{
		"item_armorregen",
		"sound/items/armorregen.ogg",
        { "models/powerups/ammo.md3",
		0, 0, 0 },
/* icon */		"icons/armor_regen",
/* pickup */	"Armor Regen",
		0,
		IT_PERSISTANT_POWERUP,
		PW_AMMOREGEN,
/* precache */ "",
/* sounds */ ""
	},

	/*QUAKED team_CTF_neutralflag (0 0 1) (-16 -16 -16) (16 16 16)
Only in One Flag CTF games
*/
	{
		"team_CTF_neutralflag",
		NULL,
        { "models/flags/n_flag.md3",
		0, "models/flag3/n_flag3.md3", 0 },
/* icon */		"gfx/2d/flag_status/flag_at_base",
/* pickup */	"Neutral Flag",
		0,
		IT_TEAM,
		PW_NEUTRALFLAG,
/* precache */ "",
/* sounds */ ""
	},

	{
		"item_redcube",
		"sound/misc/am_pkup.wav",
        { "models/powerups/orb/r_orb.md3",
		0, 0, 0 },
/* icon */		"icons/iconh_rorb",
/* pickup */	"Red Skull",
		0,
		IT_TEAM,
		0,
/* precache */ "",
/* sounds */ ""
	},

	{
		"item_bluecube",
		"sound/misc/am_pkup.wav",
        { "models/powerups/orb/b_orb.md3",
		0, 0, 0 },
/* icon */		"icons/iconh_borb",
/* pickup */	"Blue Skull",
		0,
		IT_TEAM,
		0,
/* precache */ "",
/* sounds */ ""
	},
/*QUAKED weapon_nailgun (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_nailgun", 
		"sound/misc/w_pkup.wav",
        { "models/weapons/nailgun/nailgun.md3", 
		0, 0, 0},
/* icon */		"icons/iconw_nailgun",
/* pickup */	"Nailgun",
		10,
		IT_WEAPON,
		ITEMTAG_WEAPON_NAILGUN,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED weapon_prox_launcher (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_prox_launcher", 
		"sound/misc/w_pkup.wav",
        { "models/weapons/proxmine/proxmine.md3", 
		0, 0, 0},
/* icon */		"icons/iconw_proxlauncher",
/* pickup */	"Prox Launcher",
		5,
		IT_WEAPON,
		ITEMTAG_WEAPON_PROX_LAUNCHER,
/* precache */ "",
/* sounds */ "sound/weapons/proxmine/wstbtick.wav "
			"sound/weapons/proxmine/wstbactv.wav "
			"sound/weapons/proxmine/wstbimpl.wav "
			"sound/weapons/proxmine/wstbimpm.wav "
			"sound/weapons/proxmine/wstbimpd.wav "
			"sound/weapons/proxmine/wstbactv.wav"
	},

/*QUAKED weapon_chaingun (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_chaingun", 
		"sound/misc/w_pkup.wav",
        { "models/weapons/vulcan/vulcan.md3", 
		0, 0, 0},
/* icon */		"icons/iconw_chaingun",
/* pickup */	"Chaingun",
		100,	// QL ammo pickup (Q3 default: 80)
		IT_WEAPON,
		ITEMTAG_WEAPON_CHAINGUN,
/* precache */ "",
/* sounds */ "sound/weapons/vulcan/wvulwind.wav"
	},

	{
		"item_spawnarmor",
		NULL,
		{ 0, 0, 0, 0 },
/* icon */		"icons/spawnarmor",
/* pickup */	"Spawn Armor",
		0,
		IT_POWERUP,
		0,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED weapon_hmg (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"weapon_hmg",
		"sound/misc/w_pkup.wav",
        { "models/weapons3/hmg/hmg.md3",
		0, 0, 0},
/* icon */		"icons/weap_hmg",
/* pickup */	"Heavy Machinegun",
		100,
		IT_WEAPON,
		ITEMTAG_WEAPON_HEAVY_MACHINEGUN,
/* precache */ "",
/* sounds */ ""
	},

/*QUAKED ammo_hmg (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"ammo_hmg",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/hmgam.md3",
		0, 0, 0},
/* icon */		"icons/ammo_hmg",
/* pickup */	"Heavy Bullets",
		50,
		IT_AMMO,
		ITEMTAG_WEAPON_HEAVY_MACHINEGUN,
/* precache */ "",
/* sounds */ ""
	},

	{
		"ammo_pack",
		"sound/misc/am_pkup.wav",
        { "models/powerups/ammo/ammopack.md3",
		0, 0, 0},
/* icon */		"icons/ammo_pack",
/* pickup */	"Ammo Pack",
		1,
		IT_AMMO,
		WP_NUM_WEAPONS,
/* precache */ "",
/* sounds */ ""
	},

	//
	// KEY ITEMS
	//
/*QUAKED item_key_silver (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_key_silver",
		"sound/items/key_silver.wav",
        { "models/powerups/keys/key_silver.md3",
		0, 0, 0},
/* icon */		"icons/key_silver",
/* pickup */	"Silver Key",
		1,
		IT_KEY,
		KEY_FLAG_SILVER,
/* precache */ "",
/* sounds */ ""
	},
/*QUAKED item_key_gold (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_key_gold",
		"sound/items/key_gold.wav",
        { "models/powerups/keys/key_gold.md3",
		0, 0, 0},
/* icon */		"icons/key_gold",
/* pickup */	"Gold Key",
		1,
		IT_KEY,
		KEY_FLAG_GOLD,
/* precache */ "",
/* sounds */ ""
	},
/*QUAKED item_key_master (.3 .3 1) (-16 -16 -16) (16 16 16) suspended
*/
	{
		"item_key_master",
		"sound/items/key_gold.wav",
        { "models/powerups/keys/key_master.md3",
		0, 0, 0},
/* icon */		"icons/key_master",
/* pickup */	"Master Key",
		1,
		IT_KEY,
		KEY_FLAG_MASTER,
/* precache */ "",
/* sounds */ ""
	},

	// end of list marker
	{NULL}
};

int		bg_numItems = sizeof(bg_itemlist) / sizeof(bg_itemlist[0]) - 1;

/*
==============
BG_IsTeamFlagItem

Returns qtrue when the supplied item row is one of the three CTF flag items.
==============
*/
static qboolean BG_IsTeamFlagItem( const gitem_t *item ) {
	if ( !item ) {
		return qfalse;
	}

	if ( item->giType != IT_TEAM ) {
		return qfalse;
	}

	return (qboolean)( item->giTag == PW_REDFLAG || item->giTag == PW_BLUEFLAG || item->giTag == PW_NEUTRALFLAG );
}

/*
==============
BG_FindItemByTypeAndTag

Shared retail item-table lookup keyed by item type and tag.
==============
*/
gitem_t	*BG_FindItemByTypeAndTag( itemType_t type, int tag ) {
	gitem_t	*it;

	for ( it = bg_itemlist + 1 ; it->classname ; it++ ) {
		if ( it->giType == type && it->giTag == tag ) {
			return it;
		}
	}

	Com_Error( ERR_DROP, "Couldn't find item for type %i tag %i", type, tag );
	return NULL;
}

/*
==============
BG_FindItemForPowerup
==============
*/
gitem_t	*BG_FindItemForPowerup( powerup_t pw ) {
	int		i;

	if ( pw <= PW_NONE || pw >= PW_NUM_POWERUPS ) {
		return NULL;
	}

	if ( pw == PW_INVULNERABILITY ) {
		return BG_FindItemForHoldable( HI_INVULNERABILITY );
	}

	if ( pw == PW_SCOUT || pw == PW_GUARD || pw == PW_DOUBLER || pw == PW_AMMOREGEN ) {
		for ( i = 0 ; i < bg_numItems ; i++ ) {
			if ( bg_itemlist[i].giType == IT_PERSISTANT_POWERUP && bg_itemlist[i].giTag == pw ) {
				return &bg_itemlist[i];
			}
		}

		Com_Error( ERR_DROP, "BG_FindItemForPowerup: couldn't find TA rune %i", pw );
		return NULL;
	}

	for ( i = 0 ; i < bg_numItems ; i++ ) {
		if ( ( bg_itemlist[i].giType == IT_POWERUP || bg_itemlist[i].giType == IT_TEAM ) &&
			bg_itemlist[i].giTag == pw ) {
			return &bg_itemlist[i];
		}
	}

	Com_Error( ERR_DROP, "BG_FindItemForPowerup: couldn't find item for powerup %i", pw );
	return NULL;
}


/*
==============
BG_FindItemForHoldable
==============
*/
gitem_t	*BG_FindItemForHoldable( holdable_t pw ) {
	int	holdableTag;

	holdableTag = BG_ItemTagForHoldable( pw );

	return BG_FindItemByTypeAndTag( IT_HOLDABLE, holdableTag );
}


/*
===============
BG_FindItemForWeapon

===============
*/
gitem_t	*BG_FindItemForWeapon( weapon_t weapon ) {
	int	weaponTag;

	weaponTag = BG_ItemTagForWeapon( weapon );

	return BG_FindItemByTypeAndTag( IT_WEAPON, weaponTag );
}

/*
===============
BG_FindItem

===============
*/
gitem_t	*BG_FindItem( const char *pickupName ) {
	gitem_t	*it;
	
	for ( it = bg_itemlist + 1 ; it->classname ; it++ ) {
		if ( !Q_stricmp( it->pickup_name, pickupName ) )
			return it;
	}

	return NULL;
}

/*
===============
BG_FindItemByClassname
===============
*/
gitem_t *BG_FindItemByClassname( const char *className ) {
	gitem_t *it;

	if ( !className || !*className ) {
		return NULL;
	}

	for ( it = bg_itemlist + 1 ; it->classname ; it++ ) {
		if ( !Q_stricmp( it->classname, className ) ) {
			return it;
		}
	}

	return NULL;
}

/*
===============
BG_WeaponName

Returns the retail user-facing label for the supplied weapon enum.
===============
*/
const char *BG_WeaponName( weapon_t weapon ) {
	int	weaponTag;

	weaponTag = BG_ItemTagForWeapon( weapon );
	if ( weaponTag <= WP_NONE || weaponTag >= WP_NUM_WEAPONS ) {
		return bg_retailWeaponNames[WP_NONE];
	}

	if ( !bg_retailWeaponNames[weaponTag] ) {
		return bg_retailWeaponNames[WP_NONE];
	}

	return bg_retailWeaponNames[weaponTag];
}

/*
============
BG_PlayerTouchesItem

Items can be picked up without actually touching their physical bounds to make
grabbing them easier
============
*/
qboolean	BG_PlayerTouchesItem( playerState_t *ps, entityState_t *item, int atTime ) {
	vec3_t		origin;
	const gitem_t	*itemDef;
	float		maxZDelta;

	BG_EvaluateTrajectory( &item->pos, atTime, origin );
	itemDef = NULL;
	maxZDelta = 29.0f;

	if ( item->modelindex > 0 && item->modelindex < bg_numItems ) {
		itemDef = &bg_itemlist[item->modelindex];

		if ( BG_IsTeamFlagItem( itemDef ) ) {
			maxZDelta = 64.0f;
		}
	}

	// we are ignoring ducked differences here
	if ( ps->origin[0] - origin[0] > 36
		|| ps->origin[0] - origin[0] < -36
		|| ps->origin[1] - origin[1] > 36
		|| ps->origin[1] - origin[1] < -36
		|| ps->origin[2] - origin[2] > maxZDelta
		|| ps->origin[2] - origin[2] < -50 ) {
		return qfalse;
	}

	return qtrue;
}




/*
=============
BG_IsDroppedItem

Checks whether the network state describes a dropped pickup rather than a
map-spawned instance.
=============
*/
static qboolean BG_IsDroppedItem( const entityState_t *ent ) {
	return ( ent->modelindex2 != 0 );
}

/*
=============
BG_IsArmorTieredModeEnabled

Resolves the module-local cvar that mirrors the retail tiered armor toggle.
=============
*/
static qboolean BG_IsArmorTieredModeEnabled( void ) {
#ifdef CGAME
	return cg_armorTiered.integer ? qtrue : qfalse;
#elif defined(QAGAME)
	return g_armorTiered.integer ? qtrue : qfalse;
#else
	return qfalse;
#endif
}

/*
=============
BG_CanGrabWeaponItem

Preserves the retail weapon-touch leaf: ironsights block pickups, dropped
weapons stay pickupable, and world weapons only regrab when the player does
not already own them or has run dry on ammo.
=============
*/
static qboolean BG_CanGrabWeaponItem( int gametype, int currentTime, const entityState_t *ent, const playerState_t *ps, const gitem_t *item, qboolean dropped )
{
	int	weapon;

	if ( !ps || !item ) {
		return qfalse;
	}

	if ( ps->pm_flags & PMF_IRONSIGHTS ) {
		return qfalse;
	}

	if ( dropped ) {
		return qtrue;
	}

	(void)gametype;
	(void)currentTime;
	(void)ent;

	weapon = BG_WeaponForItemTag( item->giTag );
	if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return qfalse;
	}

	if ( !( ps->stats[STAT_WEAPONS] & ( 1 << weapon ) ) ) {
		return qtrue;
	}

	return ( ps->ammo[weapon] <= 0 ) ? qtrue : qfalse;
}

/*
=============
BG_CanGrabArmorItem

Implements the tiered armor pickup checks used by the DLL's case tables.
=============
*/
static qboolean BG_CanGrabArmorItem( int gametype, int currentTime, const entityState_t *ent, const playerState_t *ps, const gitem_t *item, qboolean dropped )
{
	const int	armor = ps ? ps->stats[STAT_ARMOR] : 0;

	if ( !ps || !item ) {
		return qfalse;
	}

	(void)gametype;
	(void)currentTime;
	(void)ent;
	(void)dropped;

	if ( item->quantity == 100 ) {
		return ( armor < 200 ) ? qtrue : qfalse;
	}

	if ( item->quantity == 50 ) {
		if ( ps->armorTier <= 1 ) {
			return ( armor < 150 ) ? qtrue : qfalse;
		}

		return ( armor <= 132 ) ? qtrue : qfalse;
	}

	if ( item->quantity == 25 ) {
		if ( ps->armorTier == 0 ) {
			return ( armor < 100 ) ? qtrue : qfalse;
		}

		if ( ps->armorTier == 1 ) {
			return ( armor <= 75 ) ? qtrue : qfalse;
		}

		return ( armor <= 66 ) ? qtrue : qfalse;
	}

	return ( armor < BG_GetArmorUpperBound( ps ) ) ? qtrue : qfalse;
}

/*
=============
BG_CanGrabHealthItem

Shared retail health-pickup helper called from BG_CanItemBeGrabbed.
=============
*/
static qboolean BG_CanGrabHealthItem( int gametype, int currentTime, const entityState_t *ent, const playerState_t *ps, const gitem_t *item, qboolean dropped ) {
	int	upperBound;

	upperBound = BG_GetHealthUpperBound( ps, item->quantity );
	if ( upperBound <= 0 ) {
		return qfalse;
	}

	return ( ps->stats[STAT_HEALTH] < upperBound ) ? qtrue : qfalse;
}

/*
=============
BG_PlayerCarryingFlag

Returns qtrue when the player currently carries any team-flag powerup.
=============
*/
qboolean BG_PlayerCarryingFlag( const playerState_t *ps ) {
	if ( ps->powerups[PW_REDFLAG] ) {
		return qtrue;
	}
	if ( ps->powerups[PW_BLUEFLAG] ) {
		return qtrue;
	}
	if ( ps->powerups[PW_NEUTRALFLAG] ) {
		return qtrue;
	}

	return qfalse;
}

/*
================
BG_CanItemBeGrabbed

Returns false if the item should not be picked up.
This needs to be the same for client side prediction and server use.
================
*/
qboolean BG_CanItemBeGrabbed( int gametype, int currentTime, const entityState_t *ent, const playerState_t *ps ) {
	gitem_t		*item;
	int		weapon;
	int		maxAmmo;
	qboolean	carryingAnyFlag;
	const qboolean dropped = BG_IsDroppedItem( ent );

	if ( ent->modelindex < 1 || ent->modelindex >= bg_numItems ) {
		Com_Error( ERR_DROP, "BG_CanItemBeGrabbed: index out of range" );
	}

	item = &bg_itemlist[ent->modelindex];

	if ( dropped && ps->clientNum == ent->otherEntityNum && currentTime < ent->time2 + 1000 ) {
		return qfalse;
	}

	if ( item->giType < IT_BAD || item->giType > IT_KEY ) {
		Com_Error( ERR_DROP, "BG_CanItemBeGrabbed: invalid item type %d", item->giType );
	}

	switch ( item->giType ) {
	case IT_WEAPON:
		return BG_CanGrabWeaponItem( gametype, currentTime, ent, ps, item, dropped );

	case IT_AMMO:
		if ( gametype == GT_DOMINATION ) {
			return qtrue;
		}

		if ( dropped ) {
			return qtrue;
		}

		if ( item->giTag == WP_NUM_WEAPONS ) {
			for ( weapon = WP_MACHINEGUN ; weapon < WP_NUM_WEAPONS ; weapon++ ) {
				maxAmmo = BG_GetWeaponMaxAmmo( weapon );
				if ( maxAmmo <= 0 ) {
					continue;
				}

				if ( !( ps->stats[STAT_WEAPONS] & ( 1 << weapon ) ) ) {
					continue;
				}

				if ( ps->ammo[weapon] < maxAmmo ) {
					return qtrue;
				}
			}

			return qfalse;
		}

		weapon = BG_WeaponForItemTag( item->giTag );
		if ( weapon <= WP_NONE || weapon >= WP_NUM_WEAPONS ) {
			return qfalse;
		}

		return ( ps->ammo[weapon] < BG_GetWeaponMaxAmmo( weapon ) ) ? qtrue : qfalse;

	case IT_ARMOR:
		if ( !BG_IsArmorTieredModeEnabled() ) {
			return ( ps->stats[STAT_ARMOR] < BG_GetArmorUpperBound( ps ) ) ? qtrue : qfalse;
		}

		return BG_CanGrabArmorItem( gametype, currentTime, ent, ps, item, dropped );

	case IT_HEALTH:
		return BG_CanGrabHealthItem( gametype, currentTime, ent, ps, item, dropped );

	case IT_POWERUP:
		return qtrue;

	case IT_HOLDABLE:
		return ( ps->stats[STAT_HOLDABLE_ITEM] == 0 ) ? qtrue : qfalse;

	case IT_PERSISTANT_POWERUP:
		if ( ps->stats[STAT_PERSISTANT_POWERUP] ) {
			return qfalse;
		}

		if ( ( ent->generic1 & 2 ) && ( ps->persistant[PERS_TEAM] != TEAM_RED ) ) {
			return qfalse;
		}
		if ( ( ent->generic1 & 4 ) && ( ps->persistant[PERS_TEAM] != TEAM_BLUE ) ) {
			return qfalse;
		}

		return qtrue;

	case IT_TEAM:
		carryingAnyFlag = BG_PlayerCarryingFlag( ps );

		switch ( gametype ) {
		case GT_CTF:
			if ( ps->persistant[PERS_TEAM] == TEAM_RED ) {
				if ( item->giTag == PW_BLUEFLAG ) {
					return carryingAnyFlag ? qfalse : qtrue;
				}

				if ( item->giTag == PW_REDFLAG ) {
					if ( ps->powerups[PW_BLUEFLAG] ) {
						return qtrue;
					}

					return dropped && !ps->powerups[PW_NEUTRALFLAG] && !ps->powerups[PW_REDFLAG];
				}
			}
			else if ( ps->persistant[PERS_TEAM] == TEAM_BLUE ) {
				if ( item->giTag == PW_REDFLAG ) {
					return carryingAnyFlag ? qfalse : qtrue;
				}

				if ( item->giTag == PW_BLUEFLAG ) {
					if ( ps->powerups[PW_REDFLAG] ) {
						return qtrue;
					}

					return dropped && !ps->powerups[PW_NEUTRALFLAG] && !ps->powerups[PW_BLUEFLAG];
				}
			}
			break;

		case GT_1FCTF:
			if ( item->giTag == PW_NEUTRALFLAG ) {
				return carryingAnyFlag ? qfalse : qtrue;
			}

			if ( ps->persistant[PERS_TEAM] == TEAM_RED ) {
				if ( item->giTag == PW_BLUEFLAG ) {
					return ps->powerups[PW_NEUTRALFLAG] ? qtrue : qfalse;
				}

				if ( item->giTag == PW_REDFLAG ) {
					if ( dropped ) {
						return qtrue;
					}

					return ps->powerups[PW_NEUTRALFLAG] ? qtrue : qfalse;
				}
			}
			else if ( ps->persistant[PERS_TEAM] == TEAM_BLUE ) {
				if ( item->giTag == PW_REDFLAG ) {
					return ps->powerups[PW_NEUTRALFLAG] ? qtrue : qfalse;
				}

				if ( item->giTag == PW_BLUEFLAG ) {
					if ( dropped ) {
						return qtrue;
					}

					return ps->powerups[PW_NEUTRALFLAG] ? qtrue : qfalse;
				}
			}
			break;

		case GT_HARVESTER:
			return qtrue;

		case GT_ATTACK_DEFEND:
			if ( dropped ) {
				return qfalse;
			}

			if ( ps->persistant[PERS_TEAM] == TEAM_RED ) {
				if ( item->giTag == PW_BLUEFLAG ) {
					return qtrue;
				}

				if ( item->giTag == PW_REDFLAG ) {
					return ps->powerups[PW_BLUEFLAG] ? qtrue : qfalse;
				}
			}
			else if ( ps->persistant[PERS_TEAM] == TEAM_BLUE ) {
				if ( item->giTag == PW_REDFLAG ) {
					return qtrue;
				}

				if ( item->giTag == PW_BLUEFLAG ) {
					return ps->powerups[PW_REDFLAG] ? qtrue : qfalse;
				}
			}
			break;

		default:
			break;
		}

		return qfalse;

	case IT_KEY:
		return qtrue;

	default:
		break;
	}

	return qfalse;
}

//======================================================================

/*
================
BG_TrajectoryAcceleration

Returns the Quake Live acceleration scalar stored immediately after trDelta
by retail type-6 trajectory callers.
================
*/
static float BG_TrajectoryAcceleration( const trajectory_t *tr ) {
	const float	*acceleration;

	acceleration = (const float *)(const void *)( (const byte *)tr + sizeof( *tr ) );
	return *acceleration;
}

/*
================
BG_EvaluateTrajectory

================
*/
void BG_EvaluateTrajectory( const trajectory_t *tr, int atTime, vec3_t result ) {
	float		deltaTime;
	float		phase;

	switch( tr->trType ) {
	case TR_STATIONARY:
	case TR_INTERPOLATE:
		VectorCopy( tr->trBase, result );
		break;
	case TR_LINEAR:
		deltaTime = ( atTime - tr->trTime ) * 0.001;	// milliseconds to seconds
		VectorMA( tr->trBase, deltaTime, tr->trDelta, result );
		break;
	case TR_SINE:
		deltaTime = ( atTime - tr->trTime ) / (float) tr->trDuration;
		phase = sin( deltaTime * M_PI * 2 );
		VectorMA( tr->trBase, phase, tr->trDelta, result );
		break;
	case TR_LINEAR_STOP:
		if ( atTime > tr->trTime + tr->trDuration ) {
			atTime = tr->trTime + tr->trDuration;
		}
		deltaTime = ( atTime - tr->trTime ) * 0.001;	// milliseconds to seconds
		if ( deltaTime < 0 ) {
			deltaTime = 0;
		}
		VectorMA( tr->trBase, deltaTime, tr->trDelta, result );
		break;
	case TR_GRAVITY:
		deltaTime = ( atTime - tr->trTime ) * 0.001;	// milliseconds to seconds
		VectorMA( tr->trBase, deltaTime, tr->trDelta, result );
		result[2] -= 0.5 * DEFAULT_GRAVITY * deltaTime * deltaTime;		// FIXME: local gravity...
		break;
	case TR_QL_ACCEL:
		deltaTime = ( atTime - tr->trTime ) * 0.001;	// milliseconds to seconds
		VectorMA( tr->trBase, deltaTime, tr->trDelta, result );
		result[2] -= 0.5 * BG_TrajectoryAcceleration( tr ) * deltaTime * deltaTime;
		break;
	default:
		Com_Error( ERR_DROP, "BG_EvaluateTrajectory: unknown trType: %i", tr->trTime );
		break;
	}
}

/*
================
BG_EvaluateTrajectoryDelta

For determining velocity at a given time
================
*/
void BG_EvaluateTrajectoryDelta( const trajectory_t *tr, int atTime, vec3_t result ) {
	float	deltaTime;
	float	phase;

	switch( tr->trType ) {
	case TR_STATIONARY:
	case TR_INTERPOLATE:
		VectorClear( result );
		break;
	case TR_LINEAR:
		VectorCopy( tr->trDelta, result );
		break;
	case TR_SINE:
		deltaTime = ( atTime - tr->trTime ) / (float) tr->trDuration;
		phase = cos( deltaTime * M_PI * 2 );	// derivative of sin = cos
		phase *= 0.5;
		VectorScale( tr->trDelta, phase, result );
		break;
	case TR_LINEAR_STOP:
		if ( atTime > tr->trTime + tr->trDuration ) {
			VectorClear( result );
			return;
		}
		VectorCopy( tr->trDelta, result );
		break;
	case TR_GRAVITY:
		deltaTime = ( atTime - tr->trTime ) * 0.001;	// milliseconds to seconds
		VectorCopy( tr->trDelta, result );
		result[2] -= DEFAULT_GRAVITY * deltaTime;		// FIXME: local gravity...
		break;
	case TR_QL_ACCEL:
		deltaTime = ( atTime - tr->trTime ) * 0.001;	// milliseconds to seconds
		VectorCopy( tr->trDelta, result );
		result[2] -= BG_TrajectoryAcceleration( tr ) * deltaTime;
		break;
	default:
		Com_Error( ERR_DROP, "BG_EvaluateTrajectoryDelta: unknown trType: %i", tr->trTime );
		break;
	}
}

char *eventnames[] = {
	"EV_NONE",

	"EV_FOOTSTEP",
	"EV_FOOTSTEP_METAL",
	"EV_FOOTSPLASH",
	"EV_FOOTWADE",
	"EV_SWIM",

	"EV_FALL_SHORT",
	"EV_FALL_MEDIUM",
	"EV_FALL_FAR",

	"EV_JUMP_PAD",

	"EV_JUMP",
	"EV_WATER_TOUCH",	// foot touches
	"EV_WATER_LEAVE",	// foot leaves
	"EV_WATER_UNDER",	// head touches
	"EV_WATER_CLEAR",	// head leaves

	"EV_ITEM_PICKUP",			// normal item pickups are predictable
	"EV_GLOBAL_ITEM_PICKUP",	// powerup / team sounds are broadcast to everyone

	"EV_NOAMMO",
	"EV_CHANGE_WEAPON",
	"EV_DROP_WEAPON",
	"EV_FIRE_WEAPON",

	"EV_USE_ITEM0",
	"EV_USE_ITEM1",
	"EV_USE_ITEM2",
	"EV_USE_ITEM3",
	"EV_USE_ITEM4",
	"EV_USE_ITEM5",
	"EV_USE_ITEM6",
	"EV_USE_ITEM7",
	"EV_USE_ITEM8",
	"EV_USE_ITEM9",
	"EV_USE_ITEM10",
	"EV_USE_ITEM11",
	"EV_USE_ITEM12",
	"EV_USE_ITEM13",
	"EV_USE_ITEM14",
	"EV_UNUSED_24",

	"EV_ITEM_RESPAWN",
	"EV_ITEM_POP",
	"EV_PLAYER_TELEPORT_IN",
	"EV_PLAYER_TELEPORT_OUT",

	"EV_GRENADE_BOUNCE",		// eventParm will be the soundindex

	"EV_GENERAL_SOUND",
	"EV_GLOBAL_SOUND",		// no attenuation
	"EV_GLOBAL_TEAM_SOUND",

	"EV_BULLET_HIT_FLESH",
	"EV_BULLET_HIT_WALL",

	"EV_MISSILE_HIT",
	"EV_MISSILE_MISS",
	"EV_MISSILE_MISS_METAL",
	"EV_RAILTRAIL",
	"EV_SHOTGUN",
	"EV_UNUSED_34",

	"EV_PAIN",
	"EV_DEATH1",
	"EV_DEATH2",
	"EV_DEATH3",
	"EV_DROWN",
	"EV_OBITUARY",

	"EV_POWERUP_QUAD",
	"EV_POWERUP_BATTLESUIT",
	"EV_POWERUP_REGEN",
	"EV_POWERUP_ARMORREGEN",

	"EV_GIB_PLAYER",			// gib a previously living player
	"EV_SCOREPLUM",			// score plum

	"EV_PROXIMITY_MINE_STICK",
	"EV_PROXIMITY_MINE_TRIGGER",
	"EV_KAMIKAZE",			// kamikaze explodes
	"EV_OBELISKEXPLODE",		// obelisk explodes
	"EV_OBELISKPAIN",
	"EV_INVUL_IMPACT",		// invulnerability sphere impact
	"EV_JUICED",				// invulnerability juiced effect
	"EV_LIGHTNINGBOLT",		// lightning bolt bounced off invulnerability sphere

	"EV_DEBUG_LINE",
	"EV_TAUNT",
	"EV_TAUNT_YES",
	"EV_TAUNT_NO",
	"EV_TAUNT_FOLLOWME",
	"EV_TAUNT_GETFLAG",
	"EV_TAUNT_GUARDBASE",
	"EV_TAUNT_PATROL",
	"EV_FOOTSTEP_SNOW",
	"EV_FOOTSTEP_WOOD",
	"EV_ITEM_PICKUP_SPEC",
	"EV_OVERTIME",
	"EV_GAMEOVER",
	"EV_MISSILE_MISS_DMGTHROUGH",
	"EV_THAW_PLAYER",
	"EV_THAW_TICK",
	"EV_SHOTGUN_KILL",
	"EV_POI",
	"EV_UNUSED_5B",
	"EV_LIGHTNING_DISCHARGE",
	"EV_RACE_START",
	"EV_RACE_CHECKPOINT",
	"EV_RACE_FINISH",
	"EV_DAMAGEPLUM",
	"EV_AWARD",
	"EV_INFECTED",
	"EV_NEW_HIGH_SCORE"

};

/*
===============
BG_AddPredictableEventToPlayerstate

Handles the sequence numbers
===============
*/

void	trap_Cvar_VariableStringBuffer( const char *var_name, char *buffer, int bufsize );

void BG_AddPredictableEventToPlayerstate( int newEvent, int eventParm, playerState_t *ps ) {

#ifdef _DEBUG
	{
		char buf[256];
		trap_Cvar_VariableStringBuffer("showevents", buf, sizeof(buf));
		if ( atof(buf) != 0 ) {
#ifdef QAGAME
			Com_Printf(" game event svt %5d -> %5d: num = %20s parm %d\n", ps->pmove_framecount/*ps->commandTime*/, ps->eventSequence, eventnames[newEvent], eventParm);
#else
			Com_Printf("Cgame event svt %5d -> %5d: num = %20s parm %d\n", ps->pmove_framecount/*ps->commandTime*/, ps->eventSequence, eventnames[newEvent], eventParm);
#endif
		}
	}
#endif
	ps->events[ps->eventSequence & (MAX_PS_EVENTS-1)] = newEvent;
	ps->eventParms[ps->eventSequence & (MAX_PS_EVENTS-1)] = eventParm;
	ps->eventSequence++;
}

/*
========================
BG_TouchJumpPad
========================
*/
void BG_TouchJumpPad( playerState_t *ps, entityState_t *jumppad ) {
	// spectators don't use jump pads
	if ( ps->pm_type != PM_NORMAL ) {
		return;
	}

	// flying characters don't hit bounce pads
	if ( ps->powerups[PW_FLIGHT] ) {
		return;
	}

	// if we didn't hit this same jumppad the previous frame
	// then don't play the event sound again if we are in a fat trigger
	if ( ps->jumppad_ent != jumppad->number ) {
		// Retail always emits the shared jump-pad event with parm 0 here.
		BG_AddPredictableEventToPlayerstate( EV_JUMP_PAD, 0, ps );
	}
	// remember hitting this jumppad this frame
	ps->jumppad_ent = jumppad->number;
	ps->jumppad_frame = ps->pmove_framecount;
	// give the player the velocity from the jumppad
	VectorCopy( jumppad->origin2, ps->velocity );
}

/*
========================
BG_ShouldClearJumpPadLaunch

Returns whether the cached jump-pad launch marker has outlived the current
upward launch arc and can be cleared.
========================
*/
qboolean BG_ShouldClearJumpPadLaunch( const playerState_t *ps ) {
	if ( !ps ) {
		return qfalse;
	}

	if ( ps->jumppad_ent == 0 ) {
		return qfalse;
	}

	if ( ps->jumppad_frame == ps->pmove_framecount ) {
		return qfalse;
	}

	if ( ps->velocity[2] > 0.0f ) {
		return qfalse;
	}

	return qtrue;
}

/*
========================
BG_PlayerStateToEntityState

This is done after each set of usercmd_t on the server,
and after local prediction on the client
========================
*/
void BG_PlayerStateToEntityState( playerState_t *ps, entityState_t *s, qboolean snap ) {
	int		i;

	if ( ps->pm_type == PM_INTERMISSION || ps->pm_type == PM_SPECTATOR ) {
		s->eType = ET_INVISIBLE;
	} else if ( ps->stats[STAT_HEALTH] <= GIB_HEALTH ) {
		s->eType = ET_INVISIBLE;
	} else {
		s->eType = ET_PLAYER;
	}

	s->number = ps->clientNum;

	s->pos.trType = TR_INTERPOLATE;
	VectorCopy( ps->origin, s->pos.trBase );
	if ( snap ) {
		SnapVector( s->pos.trBase );
	}
	// set the trDelta for flag direction
	VectorCopy( ps->velocity, s->pos.trDelta );

	s->apos.trType = TR_INTERPOLATE;
	VectorCopy( ps->viewangles, s->apos.trBase );
	if ( snap ) {
		SnapVector( s->apos.trBase );
	}

	s->angles2[YAW] = ps->movementDir;
	s->legsAnim = ps->legsAnim;
	s->torsoAnim = ps->torsoAnim;
	s->clientNum = ps->clientNum;		// ET_PLAYER looks here instead of at number
										// so corpses can also reference the proper config
	s->eFlags = ps->eFlags;
	if ( ps->stats[STAT_HEALTH] <= 0 ) {
		s->eFlags |= EF_DEAD;
	} else {
		s->eFlags &= ~EF_DEAD;
	}

	if ( ps->externalEvent ) {
		s->event = ps->externalEvent;
		s->eventParm = ps->externalEventParm;
	} else if ( ps->entityEventSequence < ps->eventSequence ) {
		int		seq;

		if ( ps->entityEventSequence < ps->eventSequence - MAX_PS_EVENTS) {
			ps->entityEventSequence = ps->eventSequence - MAX_PS_EVENTS;
		}
		seq = ps->entityEventSequence & (MAX_PS_EVENTS-1);
		s->event = ps->events[ seq ] | ( ( ps->entityEventSequence & 3 ) << 8 );
		s->eventParm = ps->eventParms[ seq ];
		ps->entityEventSequence++;
	}

	s->weapon = ps->weapon;
	s->groundEntityNum = ps->groundEntityNum;

	s->powerups = 0;
	for ( i = 0 ; i < MAX_POWERUPS ; i++ ) {
		if ( ps->powerups[ i ] ) {
			s->powerups |= 1 << i;
		}
	}

	s->loopSound = ps->loopSound;
	s->generic1 = ps->generic1;
}
