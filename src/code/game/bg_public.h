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
// bg_public.h -- definitions shared by both the server game and client game modules

#ifndef __BG_PUBLIC_H__
#define __BG_PUBLIC_H__

// because games can change separately from the main system version, we need a
// second version that must match between game and cgame

#define	GAME_VERSION		"baseqz"

#define	DEFAULT_GRAVITY		800
#define	GIB_HEALTH			-40
#define	ARMOR_PROTECTION	0.66

#define	MAX_ITEMS			256
#define	MAX_RACE_POINTS		64
#define	MAX_COUNTRY_CODE	16
#define	RACE_INVALID_TIME	0x7fffffff

#define	RANK_TIED_FLAG		0x4000

#define KEY_FLAG_SILVER         0x01
#define KEY_FLAG_GOLD           0x02
#define KEY_FLAG_MASTER         0x04

#define DEFAULT_SHOTGUN_SPREAD	700
#define DEFAULT_SHOTGUN_COUNT	20

#define	ITEM_RADIUS			15		// item sizes are needed for client side pickup detection

#define	LIGHTNING_RANGE		768

#define	SCORE_NOT_PRESENT	-9999	// for the CS_SCORES[12] when only one player is present

#define	VOTE_TIME			30000	// 30 seconds before vote times out

#define	MINS_Z				-24
#define	DEFAULT_VIEWHEIGHT	26
#define CROUCH_VIEWHEIGHT	12
#define	DEAD_VIEWHEIGHT		-16

//
// config strings are a general means of communicating variable length strings
// from the server to all connected clients.
//

// CS_SERVERINFO and CS_SYSTEMINFO are defined in q_shared.h
#define	CS_MUSIC				2
#define	CS_MESSAGE				3		// from the map worldspawn's message field
#define	CS_MOTD					4		// g_motd string for server message of the day
#define	CS_WARMUP				5		// server time when the match will be restarted
#define	CS_SCORES1				6
#define	CS_SCORES2				7
#define CS_VOTE_TIME			8
#define CS_VOTE_STRING			9
#define	CS_VOTE_YES				10
#define	CS_VOTE_NO				11

#define	CS_GAME_VERSION			12
#define	CS_LEVEL_START_TIME		13		// so the timer only shows the current level

#define CS_TEAMVOTE_TIME		14
#define CS_TEAMVOTE_STRING		16
#define	CS_TEAMVOTE_YES			18
#define	CS_TEAMVOTE_NO			20
#define	CS_INTERMISSION			22		// when 1, fraglimit/timelimit has been hit and intermission will start in a second or two
#define CS_FLAGSTATUS			23		// string indicating flag status in CTF
#define CS_SHADERSTATE			24
#define CS_BOTINFO				25
#define CS_FIRST_PLACE_NAME		0x293		// retail first-place name/token mirrored for wide placement ownerdraws
#define CS_SECOND_PLACE_NAME	0x294		// retail second-place name/token mirrored for wide placement ownerdraws
#define CS_MATCH_STATE				0x295		// timeout/overtime state info payload
#define CS_ROUND_START_TIME		0x296		// active round start time for CG_ROUNDTIMER
#define CS_TIMEOUT_START_TIME		0x29D		// active timeout start time, cleared when idle
#define CS_TIMEOUT_EXPIRE_TIME		0x29E		// active timeout expiry, or 0 for indefinite pauses
#define CS_TIMEOUT_COUNT_RED		0x29F		// remaining timeout count mirrored for red/free
#define CS_TIMEOUT_COUNT_BLUE		0x2A0		// remaining timeout count mirrored for blue/free
// Auxiliary round-based team counters refreshed by retail qagame for HUD ownerdraws.
#define CS_TEAM_COUNT_RED			0x297
#define CS_TEAM_COUNT_BLUE			0x298
// CS_FORCED_COSMETICS broadcasts an info string with the following keys:
// \sb\<0|1>  - Forces the compact scoreboard tipline when set.
// \hud\<0|1> - Enables HUD coaching widgets even if players disabled them.
// \dmg\<0|1> - Advertises damage-through-surface overrides to clients.
// \atm\<str> - Optional atmosphere token mirrored from the worldspawn or server override.
#define CS_FORCED_COSMETICS		0x2B3
// Retail qagame reserves these legacy client-number slots for postgame award winners.
#define CS_AWARD_BEST_ITEMCONTROL	0x2B4
#define CS_AWARD_MOST_ACCURATE	0x2B5
#define CS_AWARD_MOST_VALUABLE	0x2B8
#define CS_AWARD_MOST_VALUABLE_OFFENSIVE	0x2B9
#define CS_AWARD_MOST_VALUABLE_DEFENSIVE	0x2BA
#define CS_AWARD_MOST_DAMAGEDEALT	0x2BB
//
// Retail qagame uses 0x2A2 for the numeric player-cylinder toggle, 0x2A3 for
// the factory-flags bitmask, and mirrors timeout, overtime, and sudden-death
// metadata through CS_MATCH_STATE; 0x2A5 and 0x2C5 remain mode-specific
// numeric configstrings.
//
#define CS_PLAYER_CYLINDERS		0x2A2		// retail numeric g_playerCylinders transport consumed by cgame
#define CS_FACTORY_FLAGS		0x2A3		// decimal bitmask describing customized factory settings
#define CS_ENABLE_BREATH		0x2A4		// global breath effect toggle
#define CS_DOMINATION_CAPTURE_TIME	0x2A5		// floating-point g_domCapTime payload
#define CS_MAP_AUTHOR		0x2A6		// primary author name lifted from the worldspawn
#define CS_MAP_AUTHOR_ALT		0x2A7		// optional secondary author (author2 key)
#define CS_SERVER_SETTINGS_INFO_A	0x2A9		// retail info string carrying server-settings flags such as armor_tiered
#define CS_SERVER_SETTINGS_INFO_B	0x2AA		// retail info string carrying server-settings scalars such as quad and gravity
#define CS_WEAPON_RELOAD_TIMES		0x2AB		// retail compact weapon refire timings slab consumed by cgame
#define CS_PLAYER_APPEARANCE		0x2AC		// retail info string carrying enforced player-model/head overrides plus scale controls
// Legacy reconstruction alias kept temporarily while the downstream cgame consumers
// move off the old spawn-hints naming.
#define CS_SPAWN_HINTS		CS_DOMINATION_CAPTURE_TIME

#define CS_ITEMS				27		// string of 0's and 1's that tell which items are present
#define CS_RED_TEAM_NAME					28
#define CS_BLUE_TEAM_NAME					29
#define	ITEM_TIMER_DEFAULT_HEIGHT	20		// default fallback height for HUD timer spacing
#define	ITEM_TIMER_MAX_HEIGHT		128		// prevent oversized HUD timer spacing from breaking layouts

#define CUSTOM_SETTING_GAUNTLET			0x00000001u
#define CUSTOM_SETTING_MACHINEGUN		0x00000002u
#define CUSTOM_SETTING_SHOTGUN			0x00000004u
#define CUSTOM_SETTING_GRENADE_LAUNCHER	0x00000008u
#define CUSTOM_SETTING_ROCKET_LAUNCHER	0x00000010u
#define CUSTOM_SETTING_LIGHTNING_GUN		0x00000020u
#define CUSTOM_SETTING_RAILGUN			0x00000040u
#define CUSTOM_SETTING_PLASMAGUN		0x00000080u
#define CUSTOM_SETTING_BFG				0x00000100u
#define CUSTOM_SETTING_GRAPPLING_HOOK	0x00000200u
#define CUSTOM_SETTING_NAILGUN			0x00000400u
#define CUSTOM_SETTING_PROX_LAUNCHER		0x00000800u
#define CUSTOM_SETTING_CHAINGUN			0x00001000u
#define CUSTOM_SETTING_AIR_CONTROL		0x00002000u
#define CUSTOM_SETTING_RAMP_JUMP		0x00004000u
#define CUSTOM_SETTING_PHYSICS			0x00008000u
#define CUSTOM_SETTING_WEAPON_SWITCHING	0x00010000u
#define CUSTOM_SETTING_INSTAGIB			0x00020000u
#define CUSTOM_SETTING_QUAD_HOG			0x00040000u
#define CUSTOM_SETTING_REGEN_HEALTH		0x00080000u
#define CUSTOM_SETTING_DROP_HEALTH		0x00100000u
#define CUSTOM_SETTING_VAMPIRIC_DAMAGE	0x00200000u
#define CUSTOM_SETTING_ITEM_SPAWNING		0x00400000u
#define CUSTOM_SETTING_HEADSHOTS		0x00800000u
#define CUSTOM_SETTING_RAIL_JUMPING		0x01000000u
#define CUSTOM_SETTING_NO_PLAYER_CLIP	0x02000000u
#define CUSTOM_SETTING_INFECTED			0x04000000u
#define CUSTOM_SETTING_LIGHTNING_DISCHARGE	0x08000000u
#define CUSTOM_SETTING_WEAPON_MASK		( CUSTOM_SETTING_GAUNTLET | CUSTOM_SETTING_MACHINEGUN | CUSTOM_SETTING_SHOTGUN | \
										  CUSTOM_SETTING_GRENADE_LAUNCHER | CUSTOM_SETTING_ROCKET_LAUNCHER | \
										  CUSTOM_SETTING_LIGHTNING_GUN | CUSTOM_SETTING_RAILGUN | CUSTOM_SETTING_PLASMAGUN | \
										  CUSTOM_SETTING_BFG | CUSTOM_SETTING_GRAPPLING_HOOK | CUSTOM_SETTING_NAILGUN | \
										  CUSTOM_SETTING_PROX_LAUNCHER | CUSTOM_SETTING_CHAINGUN )

#define CS_MODELS				32

#define FACTORY_FLAG_TIMEOUT_LENGTH		( 1 << 0 )
#define FACTORY_FLAG_TIMEOUT_COUNT		( 1 << 1 )
#define FACTORY_FLAG_OVERTIME_LENGTH	( 1 << 2 )
#define FACTORY_FLAG_SUDDEN_DEATH_ENABLED	( 1 << 3 )
#define FACTORY_FLAG_SUDDEN_DEATH_START	( 1 << 4 )
#define FACTORY_FLAG_SUDDEN_DEATH_TICK	( 1 << 5 )
#define FACTORY_FLAG_SUDDEN_DEATH_MAX		( 1 << 6 )
#define FACTORY_FLAG_SUDDEN_DEATH_INCREMENT	( 1 << 7 )
#define FACTORY_FLAG_SUDDEN_DEATH_PRINT	( 1 << 8 )
#define FACTORY_FLAG_SUDDEN_DEATH_DELAY	( 1 << 9 )
#define	CS_SOUNDS				(CS_MODELS+MAX_MODELS)
#define	CS_PLAYERS				(CS_SOUNDS+MAX_SOUNDS)
#define CS_LOCATIONS			(CS_PLAYERS+MAX_CLIENTS)
#define CS_PARTICLES			(CS_LOCATIONS+MAX_LOCATIONS)
#define CS_RACE_SCORES			0x2BC
#define CS_RACE_INFO			0x2BD
#define CS_RACE_STATUS		CS_RACE_SCORES
#define CS_PMOVE_SETTINGS		0x2BE
#define CS_MATCH_AWARDS		0x2BF		// info string announcing accuracy/perfect medals
#define CS_CUSTOM_SETTINGS		0x2C0		// serialized factory overrides broadcast at init
#define CS_ROTATION_TITLES		0x2C1		// queue of map titles/modes for the upcoming rotation
#define CS_ROTATION_CONFIGS		0x2C2		// retail intermission next-map vote counts keyed by slot index
#define CS_INTERMISSION_EXIT_STATUS	0x2C3		// retail one-shot intermission-exit latch published before ExitLevel
#define CS_SUDDENDEATH_STATUS		CS_INTERMISSION_EXIT_STATUS	// legacy reconstruction alias
#define CS_READYUP_STATUS		0x2C4		// ready-up controller state machine payload
#define CS_RR_INFECTED_SURVIVOR_PING_RATE	0x2C5		// floating-point g_rrInfectedSurvivorPingRate payload
#define CS_RACE_RECORDS		0x2C6		// race checkpoint history used by race_init
#define CS_LOADOUT_FLAGS		0x2C7		// bitmask of forced loadout toggles
#define CS_WARMUP_READY		0x2C8		// warmup ready threshold and readiness snapshot
#define CS_LOADOUT_MASK		0x2C9		// bitmask of disabled loadout entries
#define CS_SPAWN_HINTS_ALT		CS_RR_INFECTED_SURVIVOR_PING_RATE
// Tutorial/freezetip coaching strings are kept on reconstruction-local slots so the
// recovered retail award configstring block at 0x2B4/0x2B5/0x2B8-0x2BB stays intact.
#define CS_TUTORIAL_NAME		0x2CA
#define CS_TUTORIAL_TEXT		0x2CB
#define CS_FREEZE_TIP_OBJECTIVE	0x2CC
#define CS_FREEZE_TIP_THAW		0x2CD
#define CS_FREEZE_TIP_FREEZE	0x2CE
#define CS_FREEZE_TIP_SHOOT	0x2CF
#define CS_FREEZE_TIP_SUMMARY	0x2D0

#define CS_MAX					(CS_FREEZE_TIP_SUMMARY + 1)

#if (CS_MAX) > MAX_CONFIGSTRINGS
#error overflow: (CS_MAX) > MAX_CONFIGSTRINGS
#endif

typedef enum {
	GT_FFA,				// free for all
	GT_TOURNAMENT,	// one on one tournament
	GT_SINGLE_PLAYER,	// race replaces the original single player slot

	//-- team games go after this --

	GT_TEAM,			// team deathmatch
	GT_CLAN_ARENA,	// clan arena
	GT_CTF,				// capture the flag
	GT_1FCTF,
	GT_OBELISK,
	GT_HARVESTER,
	GT_FREEZE,
	GT_DOMINATION,
	GT_ATTACK_DEFEND,
	GT_RED_ROVER,
	GT_MAX_GAME_TYPE
} gametype_t;

// Quake Live repurposes the single-player slot for Race.
#define GT_RACE		GT_SINGLE_PLAYER
#define GT_CA		GT_CLAN_ARENA

typedef enum { GENDER_MALE, GENDER_FEMALE, GENDER_NEUTER } gender_t;

/*
===================================================================================

PMOVE MODULE

The pmove code takes a player_state_t and a usercmd_t and generates a new player_state_t
and some other output data.  Used for local prediction on the client game and true
movement on the server game.
===================================================================================
*/

typedef enum {
	PM_NORMAL,		// can accelerate and turn
	PM_NOCLIP,		// noclip movement
	PM_SPECTATOR,	// still run into walls
	PM_DEAD,		// no acceleration or turning, but free falling
	PM_FREEZE,		// stuck in place with no control
	PM_INTERMISSION,	// no movement or status bar
	PM_SPINTERMISSION	// no movement or status bar
} pmtype_t;

typedef enum {
	WEAPON_READY, 
	WEAPON_RAISING,
	WEAPON_DROPPING,
	WEAPON_FIRING
} weaponstate_t;

// pmove->pm_flags
#define	PMF_DUCKED			1
#define	PMF_JUMP_HELD		2
#define PMF_ATTACK_LOCKOUT	4		// round/controller fire gate
#define	PMF_BACKWARDS_JUMP	8		// go into backwards land
#define	PMF_BACKWARDS_RUN	16		// coast down to backwards run
#define	PMF_TIME_LAND		32		// pm_time is time before rejump
#define	PMF_TIME_KNOCKBACK	64		// pm_time is an air-accelerate only time
#define	PMF_TIME_WATERJUMP	128		// pm_time is waterjump
#define PMF_NO_MOVE			256		// retail advances commandTime only while set
#define	PMF_RESPAWNED		512		// clear after attack and jump buttons come up
#define	PMF_USE_ITEM_HELD	1024
#define PMF_GRAPPLE_PULL	2048	// pull towards grapple location
#define PMF_FOLLOW			4096	// spectate following another player
#define PMF_SCOREBOARD		8192	// spectate as a scoreboard
#define PMF_INVULEXPAND		16384	// invulnerability sphere set to full size
#define PMF_WEAPON_RESET	32768	// one-shot PM_Weapon reset consumed while attacking
#define PMF_AIR_CONTROL		65536	// retail alternate air-control movement profile
#define PMF_DOUBLE_JUMP		131072	// retail air double-jump movement profile
#define PMF_REQUIRE_JUMP_RELEASE	262144	// cg_autoHop/userinfo override requiring a fresh jump press
#define PMF_IRONSIGHTS		524288	// ironsight/ADS input is being held
#define PMF_CROUCH_SLIDE	1048576	// crouch slide behavior enabled; crouchSlideTime tracks remaining slide resource

#define	PMF_ALL_TIMES	(PMF_TIME_WATERJUMP|PMF_TIME_LAND|PMF_TIME_KNOCKBACK)

#define	MAXTOUCH	32
typedef struct pmove_settings_s pmove_settings_t;


typedef struct {
	// state (in / out)
	playerState_t	*ps;

	// command (in)
	usercmd_t	cmd;
	int			tracemask;			// collide against these types of surfaces
	int			debugLevel;			// if set, diagnostic output will be printed
	qboolean	noFootsteps;		// if the game is setup for no footsteps by the server
	qboolean	gauntletHit;		// true if a gauntlet attack would actually hit something

	// results (out)
	int			numtouch;
	int			touchents[MAXTOUCH];

	vec3_t		mins, maxs;			// bounding box size

	int			watertype;
	int			waterlevel;

	float		xyspeed;

	// for fixed msec Pmove
	int			pmove_fixed;
	int			pmove_msec;

	const pmove_settings_t	*pmoveSettings;

	float		stepUp;				// positive stair delta accumulated during this Pmove
	int			stepUpTime;			// command time of the latest positive stair delta

	// callbacks to test the world
	// these will be different functions during game and cgame
	void		(*trace)( trace_t *results, const vec3_t start, const vec3_t mins, const vec3_t maxs, const vec3_t end, int passEntityNum, int contentMask );
	int			(*pointcontents)( const vec3_t point, int passEntityNum );
} pmove_t;

// if a full pmove isn't done on the client, you can just update the angles
void PM_UpdateViewAngles( playerState_t *ps, const usercmd_t *cmd );
void Pmove (pmove_t *pmove);
const pmove_settings_t *PM_GetDefaultSettings( void );

//===================================================================================


// player_state->stats[] indexes
// NOTE: may not have more than 16
typedef enum {
	STAT_HEALTH,
	STAT_HOLDABLE_ITEM,
	STAT_PERSISTANT_POWERUP,
	STAT_WEAPONS,					// 16 bit fields
	STAT_ARMOR,				
	STAT_DEAD_YAW,					// look this direction when dead (FIXME: get rid of?)
	STAT_CLIENTS_READY,				// bit mask of clients wishing to exit the intermission (FIXME: configstring?)
	STAT_MAX_HEALTH,				// health / armor limit, changable by handicap
	STAT_CHAINGUN_SPINUP,			// retail chaingun spin accumulator, clamped to 0..1000
	STAT_PLAYER_ITEM_THRUST,		// retail player-item sidecar at playerState +0xe4
	STAT_PLAYER_ITEM_TIME_MAX = 10,	// retail progress-backed holdable maximum at playerState +0xe8
	STAT_PLAYER_ITEM_TIME,			// retail progress-backed holdable current value at playerState +0xec
	STAT_PLAYER_ITEM_RECHARGE,		// retail progress-backed holdable recharge rate at playerState +0xf0
	STAT_ARMOR_TIER = 14,			// retail armor tier replicated for HUD colorization
	STAT_KEY_MASK					// retail carried-key bitmask replicated for HUD icons
} statIndex_t;


// player_state->persistant[] indexes
// these fields are the only part of player_state that isn't
// cleared on respawn
// NOTE: may not have more than 16
typedef enum {
	PERS_SCORE,						// !!! MUST NOT CHANGE, SERVER AND GAME BOTH REFERENCE !!!
	PERS_HITS,						// total points damage inflicted so damage beeps can sound on change
	PERS_RANK,						// player rank or team rank
	PERS_TEAM,						// player team
	PERS_SPAWN_COUNT,				// incremented every respawn
	PERS_PLAYEREVENTS,				// 16 bits that can be flipped for events
	PERS_ATTACKER,					// clientnum of last damage inflicter
	PERS_ATTACKEE_ARMOR,			// health/armor of last person we attacked
	PERS_KILLED,					// count of the number of times you died
	// player awards tracking
	PERS_IMPRESSIVE_COUNT,			// two railgun hits in a row
	PERS_EXCELLENT_COUNT,			// two successive kills in a short amount of time
	PERS_DEFEND_COUNT,				// defend awards
	PERS_ASSIST_COUNT,				// assist awards
	PERS_GAUNTLET_FRAG_COUNT,		// kills with the guantlet
	PERS_CAPTURES,					// captures
	PERS_KILL_COUNT					// retail kill-beep counter
} persEnum_t;


// entityState_t->eFlags
#define	EF_DEAD				0x00000001		// don't draw a foe marker over players with EF_DEAD
#define EF_TICKING			0x00000002		// used to make players play the prox mine ticking sound
#define	EF_TELEPORT_BIT		0x00000004		// toggled every time the origin abruptly changes
#define	EF_AWARD_EXCELLENT	0x00000008		// draw an excellent sprite
#define EF_PLAYER_EVENT		0x00000010
#define	EF_BOUNCE			0x00000010		// for missiles
#define	EF_BOUNCE_HALF		0x00000020		// for missiles
#define	EF_AWARD_GAUNTLET	0x00000040		// draw a gauntlet sprite
#define	EF_NODRAW			0x00000080		// may have an event, but no model (unspawned items)
#define	EF_FIRING			0x00000100		// for lightning gun
#define	EF_KAMIKAZE			0x00000200
#define	EF_MOVER_STOP		0x00000400		// will push otherwise
#define EF_AWARD_CAP		0x00000800		// draw the capture sprite
#define	EF_TALK				0x00001000		// draw a talk balloon
#define	EF_CONNECTION		0x00002000		// draw a connection trouble sprite
#define	EF_VOTED			0x00004000		// already cast a vote
#define	EF_SPECTATOR_RESPAWN	0x00004000		// Quake Live spectator specresp/item-state cue
#define	EF_AWARD_IMPRESSIVE	0x00008000		// draw an impressive sprite
#define	EF_AWARD_DEFEND		0x00010000		// draw a defend sprite
#define	EF_AWARD_ASSIST		0x00020000		// draw a assist sprite
#define EF_AWARD_DENIED		0x00040000		// denied
#define EF_TEAMVOTED		0x00080000		// already cast a team vote
#define EF_READY			0x00100000		// player is ready

// NOTE: may not have more than 16
typedef enum {
	PW_NONE,

	PW_QUAD,
	PW_BATTLESUIT,
	PW_HASTE,
	PW_INVIS,
	PW_REGEN,
	PW_FLIGHT,

	PW_REDFLAG,
	PW_BLUEFLAG,
	PW_NEUTRALFLAG,

	PW_SCOUT,
	PW_GUARD,
	PW_DOUBLER,
	PW_AMMOREGEN,
	PW_INVULNERABILITY,

	PW_NUM_POWERUPS

} powerup_t;

typedef enum {
	HI_NONE,

	HI_TELEPORTER,
	HI_MEDKIT,
	HI_KAMIKAZE,
	HI_PORTAL,
	HI_INVULNERABILITY,

	HI_NUM_HOLDABLE
} holdable_t;


typedef enum {
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
	WP_HEAVY_MACHINEGUN,

	WP_NUM_WEAPONS
} weapon_t;

// Retail bg_itemlist weapon/ammo rows keep the classic Quake III ordering and
// append the Quake Live-exclusive heavy machinegun at the end.
#define ITEMTAG_WEAPON_GAUNTLET				1
#define ITEMTAG_WEAPON_MACHINEGUN			2
#define ITEMTAG_WEAPON_SHOTGUN				3
#define ITEMTAG_WEAPON_GRENADE_LAUNCHER		4
#define ITEMTAG_WEAPON_ROCKET_LAUNCHER		5
#define ITEMTAG_WEAPON_LIGHTNING			6
#define ITEMTAG_WEAPON_RAILGUN				7
#define ITEMTAG_WEAPON_PLASMAGUN			8
#define ITEMTAG_WEAPON_BFG					9
#define ITEMTAG_WEAPON_GRAPPLING_HOOK		10
#define ITEMTAG_WEAPON_NAILGUN				11
#define ITEMTAG_WEAPON_PROX_LAUNCHER		12
#define ITEMTAG_WEAPON_CHAINGUN				13
#define ITEMTAG_WEAPON_HEAVY_MACHINEGUN		14
#define ITEMTAG_HOLDABLE_TELEPORTER			1
#define ITEMTAG_HOLDABLE_MEDKIT				2
#define ITEMTAG_HOLDABLE_KAMIKAZE			3
#define ITEMTAG_HOLDABLE_PORTAL				4
#define ITEMTAG_HOLDABLE_INVULNERABILITY	6

typedef struct bgWeaponStats_s {
	weapon_t	weapon;
	int		pickupQuantity;
	int		maxStack;
	int		handicapFlags;
	float	pickupHandicapScale;
	float	armorHandicapScale;
	float	healthHandicapScale;
	float	respawnHandicapScale;
} bgWeaponStats_t;

typedef enum weaponHandicapType_e {
	HANDICAP_SCALAR_PICKUP,
	HANDICAP_SCALAR_ARMOR,
	HANDICAP_SCALAR_HEALTH,
	HANDICAP_SCALAR_RESPAWN,
	HANDICAP_SCALAR_MAX
} handicap_type_t;

typedef struct gitem_s gitem_t;

extern const bgWeaponStats_t bg_weaponStats[];
extern const int bg_weaponStatsCount;

const bgWeaponStats_t *BG_GetWeaponStats( weapon_t weapon );
int BG_GetWeaponMaxAmmo( weapon_t weapon );
float BG_GetHandicapScalar( handicap_type_t type, weapon_t weapon );
int BG_GetWeaponAmmoPackSize( weapon_t weapon );
int BG_GetWeaponAmmoPackMaxStack( weapon_t weapon );
int BG_ItemTagForWeapon( weapon_t weapon );
weapon_t BG_WeaponForItemTag( int itemTag );
int BG_ItemTagForHoldable( holdable_t holdable );
holdable_t BG_HoldableForItemTag( int itemTag );
qboolean BG_PlayerHasPersistantPowerup( const playerState_t *ps, powerup_t powerup );
int BG_GetArmorUpperBound( const playerState_t *ps );
int BG_GetHealthUpperBound( const playerState_t *ps, int pickupQuantity );
void BG_UpdateArmorTierFromCurrentArmor( playerState_t *ps, qboolean armorTiered );
void BG_ClearArmorTierIfEmpty( playerState_t *ps, qboolean armorTiered );
int BG_GetArmorRegenTarget( const playerState_t *ps, qboolean armorTiered );
void BG_ApplyArmorPickup( playerState_t *ps, const gitem_t *item, qboolean armorTiered );


struct pmove_settings_s {
	float	airAccel;
	float	airControl;
	float	airStepFriction;
	int	airSteps;
	float	airStopAccel;
	qboolean	autoHop;
	qboolean	bunnyHop;
	int	chainJump;
	float	chainJumpVelocity;
	float	circleStrafeFriction;
	qboolean	crouchSlide;
	float	crouchSlideFriction;
	int	crouchSlideTime;
	qboolean	crouchStepJump;
	qboolean	doubleJump;
	float	jumpTimeDeltaMin;
	float	jumpVelocity;
	float	jumpVelocityMax;
	float	jumpVelocityScaleAdd;
	float	jumpVelocityTimeThreshold;
	float	jumpVelocityTimeThresholdOffset;
	qboolean	noPlayerClip;
	qboolean	rampJump;
	float	rampJumpScale;
	float	stepHeight;
	qboolean	stepJump;
	float	stepJumpVelocity;
	float	strafeAccel;
	float	velocityGh;
	float	walkAccel;
	float	walkFriction;
	float	waterSwimScale;
	float	waterWadeScale;
	int	weaponDropTime;
	int	weaponRaiseTime;
	float	wishSpeed;
	float	machinegunIronsightsScale;
	float	gauntletSpeedFactor;
	int	midAirMinimumHeight;
	qboolean	nailgunBounceEnabled;
	int	nailgunBouncePercentage;
	float	quadDamageMultiplier;
	qboolean	guidedRocketEnabled;
	int	quadHogEnabled;
	int	quadHogIdleSeconds;
	int	quadHogTimeSeconds;
	int	quadHogPingRateMilliseconds;
	int	weaponReloadOverrides[WP_NUM_WEAPONS];
	int	weaponReloadTimes[WP_NUM_WEAPONS];
};


// reward sounds (stored in ps->persistant[PERS_PLAYEREVENTS])
#define	PLAYEREVENT_DENIEDREWARD		0x0001
#define	PLAYEREVENT_GAUNTLETREWARD		0x0002
#define PLAYEREVENT_HOLYSHIT			0x0004
#define PLAYEREVENT_MIDAIR			0x0008
#define PLAYEREVENT_PERFECT			0x0010
#define PLAYEREVENT_QUADGOD			0x0020
#define PLAYEREVENT_RAMPAGE			0x0040
#define PLAYEREVENT_REVENGE			0x0080
#define PLAYEREVENT_PERFORATED		0x0100
#define PLAYEREVENT_HEADSHOT		0x0200
#define PLAYEREVENT_FIRSTFRAG		0x0400

// entityState_t->event values
// entity events are for effects that take place reletive
// to an existing entities origin.  Very network efficient.

// two bits at the top of the entityState->event field
// will be incremented with each change in the event so
// that an identical event started twice in a row can
// be distinguished.  And off the value with ~EV_EVENT_BITS
// to retrieve the actual event number
#define	EV_EVENT_BIT1		0x00000100
#define	EV_EVENT_BIT2		0x00000200
#define	EV_EVENT_BITS		(EV_EVENT_BIT1|EV_EVENT_BIT2)

#define	EVENT_VALID_MSEC	300

typedef enum {
	EV_NONE = 0,

	EV_FOOTSTEP = 1,
	EV_FOOTSTEP_METAL = 2,
	EV_FOOTSPLASH = 3,
	EV_FOOTWADE = 4,
	EV_SWIM = 5,

	EV_FALL_SHORT = 6,
	EV_FALL_MEDIUM = 7,
	EV_FALL_FAR = 8,

	EV_JUMP_PAD = 9,			// boing sound at origin, jump sound on player

	EV_JUMP = 10,
	EV_WATER_TOUCH = 11,	// foot touches
	EV_WATER_LEAVE = 12,	// foot leaves
	EV_WATER_UNDER = 13,	// head touches
	EV_WATER_CLEAR = 14,	// head leaves

	EV_ITEM_PICKUP = 15,			// normal item pickups are predictable
	EV_GLOBAL_ITEM_PICKUP = 16,	// powerup / team sounds are broadcast to everyone

	EV_NOAMMO = 17,
	EV_CHANGE_WEAPON = 18,
	EV_DROP_WEAPON = 19,
	EV_FIRE_WEAPON = 20,

	EV_USE_ITEM0 = 21,
	EV_USE_ITEM1 = 22,
	EV_USE_ITEM2 = 23,
	EV_USE_ITEM3 = 24,
	EV_USE_ITEM4 = 25,
	EV_USE_ITEM5 = 26,
	EV_USE_ITEM6 = 27,
	EV_USE_ITEM7 = 28,
	EV_USE_ITEM8 = 29,
	EV_USE_ITEM9 = 30,
	EV_USE_ITEM10 = 31,
	EV_USE_ITEM11 = 32,
	EV_USE_ITEM12 = 33,
	EV_USE_ITEM13 = 34,
	EV_USE_ITEM14 = 35,
	EV_UNUSED_24 = 36,

	EV_ITEM_RESPAWN = 37,
	EV_ITEM_POP = 38,
	EV_PLAYER_TELEPORT_IN = 39,
	EV_PLAYER_TELEPORT_OUT = 40,

	EV_GRENADE_BOUNCE = 41,		// eventParm will be the soundindex

	EV_GENERAL_SOUND = 42,
	EV_GLOBAL_SOUND = 43,		// no attenuation
	EV_GLOBAL_TEAM_SOUND = 44,

	EV_BULLET_HIT_FLESH = 45,
	EV_BULLET_HIT_WALL = 46,

	EV_MISSILE_HIT = 47,
	EV_MISSILE_MISS = 48,
	EV_MISSILE_MISS_METAL = 49,
	EV_RAILTRAIL = 50,
	EV_SHOTGUN = 51,
	EV_UNUSED_34 = 52,

	EV_PAIN = 53,
	EV_DEATH1 = 54,
	EV_DEATH2 = 55,
	EV_DEATH3 = 56,
	EV_DROWN = 57,
	EV_OBITUARY = 58,

	EV_POWERUP_QUAD = 59,
	EV_POWERUP_BATTLESUIT = 60,
	EV_POWERUP_REGEN = 61,
	EV_POWERUP_ARMORREGEN = 62,

	EV_GIB_PLAYER = 63,			// gib a previously living player
	EV_SCOREPLUM = 64,			// score plum
	EV_PROXIMITY_MINE_STICK = 65,
	EV_PROXIMITY_MINE_TRIGGER = 66,
	EV_KAMIKAZE = 67,			// kamikaze explodes
	EV_OBELISKEXPLODE = 68,		// obelisk explodes
	EV_OBELISKPAIN = 69,		// obelisk is in pain
	EV_INVUL_IMPACT = 70,		// invulnerability sphere impact
	EV_JUICED = 71,				// invulnerability juiced effect
	EV_LIGHTNINGBOLT = 72,		// lightning bolt bounced off invulnerability sphere

	EV_DEBUG_LINE = 73,
	EV_TAUNT = 74,
	EV_TAUNT_YES = 75,
	EV_TAUNT_NO = 76,
	EV_TAUNT_FOLLOWME = 77,
	EV_TAUNT_GETFLAG = 78,
	EV_TAUNT_GUARDBASE = 79,
	EV_TAUNT_PATROL = 80,

	EV_FOOTSTEP_SNOW = 81,
	EV_FOOTSTEP_WOOD = 82,
	EV_ITEM_PICKUP_SPEC = 83,
	EV_OVERTIME = 84,
	EV_GAMEOVER = 85,
	EV_MISSILE_MISS_DMGTHROUGH = 86,
	EV_THAW_PLAYER = 87,
	EV_THAW_TICK = 88,
	EV_SHOTGUN_KILL = 89,
	EV_POI = 90,
	EV_UNUSED_5B = 91,
	EV_LIGHTNING_DISCHARGE = 92,
	EV_RACE_START = 93,
	EV_RACE_CHECKPOINT = 94,
	EV_RACE_FINISH = 95,
	EV_DAMAGEPLUM = 96,			// damage plum
	EV_AWARD = 97,
	EV_INFECTED = 98,
	EV_NEW_HIGH_SCORE = 99
} entity_event_t;


typedef enum {
	GTS_RED_CAPTURE = 0,
	GTS_BLUE_CAPTURE = 1,
	GTS_RED_RETURN = 2,
	GTS_BLUE_RETURN = 3,
	GTS_RED_TAKEN = 4,
	GTS_BLUE_TAKEN = 5,
	GTS_REDOBELISK_ATTACKED = 6,
	GTS_BLUEOBELISK_ATTACKED = 7,
	GTS_REDTEAM_SCORED = 8,
	GTS_BLUETEAM_SCORED = 9,
	GTS_REDTEAM_TOOK_LEAD = 10,
	GTS_BLUETEAM_TOOK_LEAD = 11,
	GTS_TEAMS_ARE_TIED = 12,
	GTS_KAMIKAZE = 13,
	GTS_REDTEAM_WINS = 14,
	GTS_BLUETEAM_WINS = 15,
	GTS_REDTEAM_WINS_ROUND = 16,
	GTS_BLUETEAM_WINS_ROUND = 17,
	GTS_ROUND_DRAW = 18,
	GTS_LAST_STANDING = 19,
	GTS_ROUND_OVER = 20,
	GTS_DOMINATION_POINT_EVENT = 23,
	GTS_SURVIVOR_WARNING = 24
} global_team_sound_t;

// animations
typedef enum {
	BOTH_DEATH1,
	BOTH_DEAD1,
	BOTH_DEATH2,
	BOTH_DEAD2,
	BOTH_DEATH3,
	BOTH_DEAD3,

	TORSO_GESTURE,

	TORSO_ATTACK,
	TORSO_ATTACK2,

	TORSO_DROP,
	TORSO_RAISE,

	TORSO_STAND,
	TORSO_STAND2,

	LEGS_WALKCR,
	LEGS_WALK,
	LEGS_RUN,
	LEGS_BACK,
	LEGS_SWIM,

	LEGS_JUMP,
	LEGS_LAND,

	LEGS_JUMPB,
	LEGS_LANDB,

	LEGS_IDLE,
	LEGS_IDLECR,

	LEGS_TURN,

	TORSO_GETFLAG,
	TORSO_GUARDBASE,
	TORSO_PATROL,
	TORSO_FOLLOWME,
	TORSO_AFFIRMATIVE,
	TORSO_NEGATIVE,

	MAX_ANIMATIONS,

	LEGS_BACKCR,
	LEGS_BACKWALK,
	FLAG_RUN,
	FLAG_STAND,
	FLAG_STAND2RUN,

	MAX_TOTALANIMATIONS
} animNumber_t;


typedef struct animation_s {
	int		firstFrame;
	int		numFrames;
	int		loopFrames;			// 0 to numFrames
	int		frameLerp;			// msec between frames
	int		initialLerp;		// msec to get to first frame
	int		reversed;			// true if animation is reversed
	int		flipflop;			// true if animation should flipflop back to base
} animation_t;


// flip the togglebit every time an animation
// changes so a restart of the same anim can be detected
#define	ANIM_TOGGLEBIT		128


typedef enum {
	TEAM_FREE,
	TEAM_RED,
	TEAM_BLUE,
	TEAM_SPECTATOR,

	TEAM_NUM_TEAMS
} team_t;

// Time between location updates
#define TEAM_LOCATION_UPDATE_TIME		1000

// How many players on the overlay
#define TEAM_MAXOVERLAY		32

//team task
typedef enum {
	TEAMTASK_NONE,
	TEAMTASK_OFFENSE, 
	TEAMTASK_DEFENSE,
	TEAMTASK_PATROL,
	TEAMTASK_FOLLOW,
	TEAMTASK_RETRIEVE,
	TEAMTASK_ESCORT,
	TEAMTASK_CAMP
} teamtask_t;

// means of death
typedef enum {
	MOD_UNKNOWN,
	MOD_SHOTGUN,
	MOD_GAUNTLET,
	MOD_MACHINEGUN,
	MOD_GRENADE,
	MOD_GRENADE_SPLASH,
	MOD_ROCKET,
	MOD_ROCKET_SPLASH,
	MOD_PLASMA,
	MOD_PLASMA_SPLASH,
	MOD_RAILGUN,
	MOD_LIGHTNING,
	MOD_BFG,
	MOD_BFG_SPLASH,
	MOD_WATER,
	MOD_SLIME,
	MOD_LAVA,
	MOD_CRUSH,
	MOD_TELEFRAG,
	MOD_FALLING,
	MOD_SUICIDE,
	MOD_TARGET_LASER,
        MOD_TRIGGER_HURT,
        MOD_NAIL,
        MOD_CHAINGUN,
        MOD_PROXIMITY_MINE,
        MOD_KAMIKAZE,
        MOD_JUICED,
        MOD_GRAPPLE,
        MOD_SWITCHTEAM,
        MOD_THAW,
        MOD_LIGHTNING_DISCHARGE,
        MOD_HMG,
        MOD_RAILGUN_HEADSHOT
} meansOfDeath_t;


//---------------------------------------------------------

// gitem_t->type
typedef enum {
	IT_BAD,
	IT_WEAPON,				// EFX: rotate + upscale + minlight
	IT_AMMO,				// EFX: rotate
	IT_ARMOR,				// EFX: rotate + minlight
	IT_HEALTH,				// EFX: static external sphere + rotating internal
	IT_POWERUP,				// instant on, timer based
							// EFX: rotate + external ring that rotates
	IT_HOLDABLE,			// single use, holdable item
							// EFX: rotate + bob
	IT_PERSISTANT_POWERUP,
	IT_TEAM,
	IT_KEY
} itemType_t;

#define MAX_ITEM_MODELS 4

struct gitem_s {
	char		*classname;	// spawning name
	char		*pickup_sound;
	char		*world_model[MAX_ITEM_MODELS];

	char		*icon;
	char		*pickup_name;	// for printing on pickup

	int			quantity;		// for ammo how much, or duration of powerup
	itemType_t  giType;			// IT_* flags

	int			giTag;

	char		*precaches;		// string of all models and images this item will use
	char		*sounds;		// string of all sounds this item will use
};

// included in both the game dll and the client
extern	gitem_t	bg_itemlist[];
extern	int		bg_numItems;

gitem_t	*BG_FindItem( const char *pickupName );
gitem_t	*BG_FindItemByClassname( const char *className );
gitem_t	*BG_FindItemByTypeAndTag( itemType_t type, int tag );
gitem_t	*BG_FindItemForWeapon( weapon_t weapon );
gitem_t	*BG_FindItemForPowerup( powerup_t pw );
gitem_t	*BG_FindItemForHoldable( holdable_t pw );
qboolean	BG_PlayerCarryingFlag( const playerState_t *ps );
const char *BG_WeaponName( weapon_t weapon );
#define	ITEM_INDEX(x) ((x)-bg_itemlist)

qboolean	BG_CanItemBeGrabbed( int gametype, int currentTime, const entityState_t *ent, const playerState_t *ps );


// g_dmflags->integer flags
#define	DF_NO_FALLING			8
#define DF_FIXED_FOV			16
#define	DF_NO_FOOTSTEPS			32

// content masks
#define	MASK_ALL				(-1)
#define	MASK_SOLID				(CONTENTS_SOLID)
#define	MASK_PLAYERSOLID		(CONTENTS_SOLID|CONTENTS_PLAYERCLIP|CONTENTS_BODY)
#define	MASK_DEADSOLID			(CONTENTS_SOLID|CONTENTS_PLAYERCLIP)
#define	MASK_WATER				(CONTENTS_WATER|CONTENTS_LAVA|CONTENTS_SLIME)
#define	MASK_OPAQUE				(CONTENTS_SOLID|CONTENTS_SLIME|CONTENTS_LAVA)
#define	MASK_SHOT				(CONTENTS_SOLID|CONTENTS_BODY|CONTENTS_CORPSE)


//
// entityState_t->eType
//
typedef enum {
	ET_GENERAL,
	ET_PLAYER,
	ET_ITEM,
	ET_MISSILE,
	ET_MOVER,
	ET_BEAM,
	ET_PORTAL,
	ET_SPEAKER,
	ET_PUSH_TRIGGER,
	ET_TELEPORT_TRIGGER,
	ET_INVISIBLE,
	ET_GRAPPLE,				// grapple hooked on wall
	ET_TEAM,

	ET_EVENTS				// any of the EV_* events can be added freestanding
							// by setting eType to ET_EVENTS + eventNum
							// this avoids having to set eFlags and eventNum
} entityType_t;



void	BG_EvaluateTrajectory( const trajectory_t *tr, int atTime, vec3_t result );
void	BG_EvaluateTrajectoryDelta( const trajectory_t *tr, int atTime, vec3_t result );

void	BG_AddPredictableEventToPlayerstate( int newEvent, int eventParm, playerState_t *ps );

void	BG_TouchJumpPad( playerState_t *ps, entityState_t *jumppad );

void	BG_PlayerStateToEntityState( playerState_t *ps, entityState_t *s, qboolean snap );

qboolean	BG_PlayerTouchesItem( playerState_t *ps, entityState_t *item, int atTime );


#define ARENAS_PER_TIER		4
#define MAX_ARENAS			1024
#define	MAX_ARENAS_TEXT		8192

#define MAX_BOTS			1024
#define MAX_BOTS_TEXT		8192


// Kamikaze

// 1st shockwave times
#define KAMI_SHOCKWAVE_STARTTIME		0
#define KAMI_SHOCKWAVEFADE_STARTTIME	1500
#define KAMI_SHOCKWAVE_ENDTIME			2000
// explosion/implosion times
#define KAMI_EXPLODE_STARTTIME			250
#define KAMI_IMPLODE_STARTTIME			2000
#define KAMI_IMPLODE_ENDTIME			2250
// 2nd shockwave times
#define KAMI_SHOCKWAVE2_STARTTIME		2000
#define KAMI_SHOCKWAVE2FADE_STARTTIME	2500
#define KAMI_SHOCKWAVE2_ENDTIME			3000
// radius of the models without scaling
#define KAMI_SHOCKWAVEMODEL_RADIUS		88
#define KAMI_BOOMSPHEREMODEL_RADIUS		72
// maximum radius of the models during the effect
#define KAMI_SHOCKWAVE_MAXRADIUS		1320
#define KAMI_BOOMSPHERE_MAXRADIUS		720
#define KAMI_SHOCKWAVE2_MAXRADIUS		704

#endif // __BG_PUBLIC_H__
