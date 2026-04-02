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
#include "../game/q_shared.h"
#include "tr_types.h"
#include "../game/bg_public.h"
#include "cg_public.h"
#include "../ui/ui_shared.h"


// The entire cgame module is unloaded and reloaded on each level change,
// so there is NO persistant data between levels on the client side.
// If you absolutely need something stored, it can either be kept
// by the server in the server stored userinfos, or stashed in a cvar.

#define CG_DEFAULT_HUD_FILE		"ui/hud3.txt"
#define CG_LEGACY_HUD_FILE		"ui/hud.txt"

#define CG_FONT_THRESHOLD 0.1

#define	POWERUP_BLINKS		5

#define	POWERUP_BLINK_TIME	1000
#define	FADE_TIME			200
#define	OBITUARY_TIME		5000
#define	MAX_OBITUARIES		16
#define	CG_OBITUARY_NAME_SIZE	40
#define	PULSE_TIME			200
#define	DAMAGE_DEFLECT_TIME	100
#define	DAMAGE_RETURN_TIME	400
#define DAMAGE_TIME			500
#define	LAND_DEFLECT_TIME	150
#define	LAND_RETURN_TIME	300
#define	STEP_TIME			200
#define	DUCK_TIME			100
#define	PAIN_TWITCH_TIME	200
#define	WEAPON_SELECT_TIME	1400
#define	ITEM_SCALEUP_TIME	1000
#define	ZOOM_TIME			150
#define	ITEM_BLOB_TIME		200
#define	MUZZLE_FLASH_TIME	20
#define	SINK_TIME			1000		// time for fragments to sink into ground before going away
#define	ATTACKER_HEAD_TIME	10000
#define	REWARD_TIME			3000

#define	PULSE_SCALE			1.5			// amount to scale up the icons when activating

#define	MAX_STEP_CHANGE		32

#define	MAX_VERTS_ON_POLY	10
#define	MAX_MARK_POLYS		256

#define STAT_MINUS			10	// num frame for '-' stats digit

#define	ICON_SIZE			48
#define	CHAR_WIDTH			32
#define	CHAR_HEIGHT			48
#define	TEXT_ICON_SPACE		4

#define	TEAMCHAT_WIDTH		80
#define TEAMCHAT_HEIGHT		8

// very large characters
#define	GIANT_WIDTH			32
#define	GIANT_HEIGHT		48

#define	NUM_CROSSHAIRS		10
#define CG_MAX_LIGHTNING_STYLES 5

#define CG_VIEW_FILTER_MAX_SAMPLES	32

#define DOM_POINT_STATE_COUNT	5
#define DOMINATION_DISTRESS_REPEAT_TIME	2000

#define TEAM_OVERLAY_MAXNAME_WIDTH	12
#define TEAM_OVERLAY_MAXLOCATION_WIDTH	16

#define	DEFAULT_MODEL			"sarge"
#define	DEFAULT_HEAD			"sarge"
#define	DEFAULT_TEAM_MODEL		"james"
#define	DEFAULT_TEAM_HEAD		"*james"

#define DEFAULT_REDTEAM_NAME		"Stroggs"
#define DEFAULT_BLUETEAM_NAME		"Pagans"

// cg_autoAction bit masks
#define CG_AUTOACTION_DEMO_RECORD	( 1 << 0 )
#define CG_AUTOACTION_SCREENSHOT	( 1 << 1 )
#define CG_AUTOACTION_STATS_UPLOAD	( 1 << 2 )

/*
=============
CG_HasObjectiveCountStat

Retail gametype predicate for the shared objective-count stat seams.
=============
*/
static ID_INLINE qboolean CG_HasObjectiveCountStat( gametype_t gametype ) {
	switch ( gametype ) {
	case GT_CTF:
	case GT_1FCTF:
	case GT_OBELISK:
	case GT_HARVESTER:
	case GT_DOMINATION:
		return qtrue;
	default:
		return qfalse;
	}
}

/*
=============
CG_IsTeamWinnerGametype

Retail gametype predicate for the shared endgame winner seams.
=============
*/
static ID_INLINE qboolean CG_IsTeamWinnerGametype( gametype_t gametype ) {
	return (qboolean)( gametype >= GT_TEAM && gametype != GT_RED_ROVER );
}

typedef enum {
	FOOTSTEP_NORMAL,
	FOOTSTEP_BOOT,
	FOOTSTEP_FLESH,
	FOOTSTEP_MECH,
	FOOTSTEP_ENERGY,
	FOOTSTEP_METAL,
	FOOTSTEP_SPLASH,

	FOOTSTEP_TOTAL
} footstep_t;

typedef enum {
	IMPACTSOUND_DEFAULT,
	IMPACTSOUND_METAL,
	IMPACTSOUND_FLESH
} impactSound_t;

typedef enum {
	DAMAGE_PLUM_PRESET_OFF,
	DAMAGE_PLUM_PRESET_ALL_WEAPONS,
	DAMAGE_PLUM_PRESET_AOE_WEAPONS,
	DAMAGE_PLUM_PRESET_CUSTOM
} damagePlumPreset_t;

typedef enum {
	DAMAGE_PLUM_COLOR_STYLE_MONOCHROME = 1,
	DAMAGE_PLUM_COLOR_STYLE_DAMAGE,
	DAMAGE_PLUM_COLOR_STYLE_WEAPON
} damagePlumColorStyle_t;

typedef enum {
	CG_SPECTATOR_TRACK_NONE = 0,
	CG_SPECTATOR_TRACK_POWERUP,
	CG_SPECTATOR_TRACK_FLAG
} cgSpectatorTrackType_t;

typedef enum {
	ROUNDSTATE_INACTIVE,
	ROUNDSTATE_WARMUP,
	ROUNDSTATE_ACTIVE,
	ROUNDSTATE_COMPLETE
} cgRoundState_t;

typedef struct {
	int		count;
	int		index;
	float	lastYaw;
	float	lastPitch;
	float	yawSamples[CG_VIEW_FILTER_MAX_SAMPLES];
	float	pitchSamples[CG_VIEW_FILTER_MAX_SAMPLES];
} cgViewAngleFilter_t;
  
typedef enum {
	ANNOUNCER_PROFILE_DISABLED = 0,
	ANNOUNCER_PROFILE_DEFAULT,
	ANNOUNCER_PROFILE_VADRIGAR,
	ANNOUNCER_PROFILE_DAEMIA,
	ANNOUNCER_PROFILE_COUNT
} cgAnnouncerProfile_t;

typedef struct {
	sfxHandle_t	oneMinuteSound;
	sfxHandle_t	fiveMinuteSound;
	sfxHandle_t	suddenDeathSound;
	sfxHandle_t	overtimeSound;
	sfxHandle_t	oneFragSound;
	sfxHandle_t	twoFragSound;
	sfxHandle_t	threeFragSound;
} cgAnnouncerSoundSet_t;

//=================================================

// player entities need to track more information
// than any other type of entity.

// note that not every player entity is a client entity,
// because corpses after respawn are outside the normal
// client numbering range

// when changing animation, set animationTime to frameTime + lerping time
// The current lerp will finish out, then it will lerp to the new animation
typedef struct {
	int			oldFrame;
	int			oldFrameTime;		// time when ->oldFrame was exactly on

	int			frame;
	int			frameTime;			// time when ->frame will be exactly on

	float		backlerp;

	float		yawAngle;
	qboolean	yawing;
	float		pitchAngle;
	qboolean	pitching;

	int			animationNumber;	// may include ANIM_TOGGLEBIT
	animation_t	*animation;
	int			animationTime;		// time when the first frame of the animation will be exact
} lerpFrame_t;


typedef struct {
	lerpFrame_t		legs, torso, flag;
	int				painTime;
	int				painDirection;	// flip from 0 to 1
	int				lightningFiring;

	// railgun trail spawning
	vec3_t			railgunImpact;
	qboolean		railgunFlash;

	// machinegun spinning
	float			barrelAngle;
	int				barrelTime;
	qboolean		barrelSpinning;
} playerEntity_t;

//=================================================


typedef struct {
	vec3_t	origin;
	char	target[MAX_QPATH];
	char	targetname[MAX_QPATH];
	qboolean	active;
} cgRacePointInfo_t;

typedef enum {
	CG_RACE_CUE_START,
	CG_RACE_CUE_CHECKPOINT,
	CG_RACE_CUE_FINISH,
	CG_RACE_CUE_COUNT
} cgRaceCue_t;

typedef struct {
	qboolean	initialized;
	qboolean	runActive;
	int		currentCheckpoint;
	int		lastTouchTime;
} cgRaceClientProgress_t;

typedef struct {
	qboolean	initialized;
	int		bestTime;
	int		lastTime;
	int		currentElapsed;
	int		lapCount;
	int		lastUpdateSequence;
} cgRaceClientStatus_t;

// centity_t have a direct corespondence with gentity_t in the game, but
// only the entityState_t is directly communicated to the cgame
typedef struct centity_s {
	entityState_t	currentState;	// from cg.frame
	entityState_t	nextState;		// from cg.nextFrame, if available
	qboolean		interpolate;	// true if next is valid to interpolate to
	qboolean		currentValid;	// true if cg.frame holds this entity

	int				muzzleFlashTime;	// move to playerEntity?
	int				previousEvent;
	int				teleportFlag;

	int				trailTime;		// so missile trails can handle dropped initial packets
	int				dustTrailTime;
	int				miscTime;

	int				snapShotTime;	// last time this entity was found in a snapshot

	playerEntity_t	pe;

	int				errorTime;		// decay the error from this time
	vec3_t			errorOrigin;
	vec3_t			errorAngles;
	
	qboolean		extrapolated;	// false if origin / angles is an interpolation
	vec3_t			rawOrigin;
	vec3_t			rawAngles;

	vec3_t			beamEnd;

	// exact interpolated position of entity on this frame
	vec3_t			lerpOrigin;
	vec3_t			lerpAngles;
} centity_t;


//======================================================================

// local entities are created as a result of events or predicted actions,
// and live independantly from all server transmitted entities

typedef struct markPoly_s {
	struct markPoly_s	*prevMark, *nextMark;
	int			time;
	qhandle_t	markShader;
	qboolean	alphaFade;		// fade alpha instead of rgb
	float		color[4];
	poly_t		poly;
	polyVert_t	verts[MAX_VERTS_ON_POLY];
} markPoly_t;


typedef enum {
	LE_MARK = 0x00,
	LE_EXPLOSION = 0x01,
	LE_SPRITE_EXPLOSION = 0x02,
	LE_FRAGMENT = 0x03,
	LE_MOVE_SCALE_FADE = 0x04,
	LE_BIGEXPLODE_TRACER = 0x05,
	LE_05 = LE_BIGEXPLODE_TRACER,		// compatibility alias for older mapping notes
	LE_FALL_SCALE_FADE = 0x06,
	LE_FADE_RGB = 0x07,
	LE_SCALE_FADE = 0x08,
	LE_SCOREPLUM = 0x09,
	LE_10 = 0x0A,
	LE_KAMIKAZE = LE_10,			// compatibility alias for the retail kamikaze producer slot
	LE_INVULIMPACT = 0x0B,
	LE_INVULJUICED = 0x0C,
	LE_SHOWREFENTITY = 0x0D,
	LE_FRAGMENT_14 = 0x0E,
	LE_DEATH_EFFECT = 0x0F,
	LE_0F = LE_DEATH_EFFECT,			// compatibility alias for older mapping notes
	LE_SCALE_FADE_OUT = LE_DEATH_EFFECT,	// compatibility alias from the older mapping pass
	LE_FRAGMENT_16 = 0x10
} leType_t;

typedef enum {
	LEF_PUFF_DONT_SCALE  = 0x0001,			// do not scale size over time
	LEF_TUMBLE			 = 0x0002,			// tumble over time, used for ejecting shells
	LEF_SOUND1			 = 0x0004,			// sound 1 for kamikaze
	LEF_SOUND2			 = 0x0008,			// sound 2 for kamikaze
	LEF_SCOREPLUM_CUSTOMCOLOR = 0x0010		// source-side retail damage-plum bridge
} leFlag_t;

typedef enum {
	LEMT_NONE = 0,
	LEMT_BURN = 1,
	LEMT_BLOOD = 2,
	LEMT_BURN_SMALL = 3,
	LEMT_ICE = 4
} leFragmentMarkType_t;		// retail fragment mark selector at localEntity + 0x98

typedef enum {
	LEBS_NONE = 0,
	LEBS_BLOOD = 1,
	LEBS_BRASS = 2,
	LEBS_ELECTRO = 3,
	LEBS_ICE = 4
} leFragmentBounceSoundType_t;	// retail fragment trail / bounce selector at localEntity + 0x9c

#define	TR_QL_ACCEL	((trType_t)6)	// retail cgame-only trajectory_t extension with a companion scalar

typedef struct localEntity_s {
	struct localEntity_s	*prev, *next;
	leType_t		leType;
	int				leFlags;

	int				startTime;
	int				endTime;
	int				fadeInTime;

	float			lifeRate;			// 1.0 / (endTime - startTime)

	trajectory_t	pos;
	trajectory_t	angles;

	float			bounceFactor;		// 0.0 = no bounce, 1.0 = perfect

	float			color[4];

	float			radius;

	float			light;
	vec3_t			lightColor;

	float			posTrajExtra;		// source-side bridge for retail pos.trajectory_t[9]
	float			anglesTrajExtra;	// source-side bridge for retail angles.trajectory_t[9]
	leFragmentMarkType_t	fragmentMarkType;
	leFragmentBounceSoundType_t fragmentBounceSoundType;

	refEntity_t		refEntity;		
} localEntity_t;

//======================================================================


typedef struct {
	int				client;
	int				score;
	int				ping;
	int				time;
	int				scoreFlags;
	int				powerUps;
	int				accuracy;
	int				impressiveCount;
	int				excellentCount;
	int				guantletCount;
	int				defendCount;
	int				assistCount;
	int				captures;
	qboolean	perfect;
	int				team;
	int				damage;
	int				deaths;
	int				kills;
	int				bestWeapon;
	int				teamDamageGiven;
	int				teamDamageReceived;
	qboolean	activePlayer;
} score_t;

typedef enum {
	CG_SCORESTAT_PICKUP_RA = 0,
	CG_SCORESTAT_PICKUP_YA,
	CG_SCORESTAT_PICKUP_GA,
	CG_SCORESTAT_PICKUP_MH,
	CG_SCORESTAT_PICKUP_COUNT
} cgScoreStatPickupIndex_t;

typedef struct {
	qboolean		valid;
	int			weaponFrags[WP_NUM_WEAPONS];
	int			weaponHits[WP_NUM_WEAPONS];
	int			weaponShots[WP_NUM_WEAPONS];
	int			weaponDamage[WP_NUM_WEAPONS];
	int			pickupCounts[CG_SCORESTAT_PICKUP_COUNT];
	float			pickupAvgSeconds[CG_SCORESTAT_PICKUP_COUNT];
	int			progressionPr;
	int			progressionTier;
} cgScoreStats_t;

typedef enum {
	CG_TEAMSTAT_MAP_PICKUPS = 0,
	CG_TEAMSTAT_PICKUPS_RA,
	CG_TEAMSTAT_PICKUPS_YA,
	CG_TEAMSTAT_PICKUPS_GA,
	CG_TEAMSTAT_PICKUPS_MH,
	CG_TEAMSTAT_PICKUPS_QUAD,
	CG_TEAMSTAT_PICKUPS_BS,
	CG_TEAMSTAT_TIMEHELD_QUAD,
	CG_TEAMSTAT_TIMEHELD_BS,
	CG_TEAMSTAT_PICKUPS_FLAG,
	CG_TEAMSTAT_PICKUPS_MEDKIT,
	CG_TEAMSTAT_PICKUPS_REGEN,
	CG_TEAMSTAT_PICKUPS_HASTE,
	CG_TEAMSTAT_PICKUPS_INVIS,
	CG_TEAMSTAT_TIMEHELD_FLAG,
	CG_TEAMSTAT_TIMEHELD_REGEN,
	CG_TEAMSTAT_TIMEHELD_HASTE,
	CG_TEAMSTAT_TIMEHELD_INVIS,
	CG_TEAMSTAT_COUNT
} cgTeamStatIndex_t;

typedef struct {
	qboolean	valid;
	int		fieldCount;
	int		values[2][CG_TEAMSTAT_COUNT];
} cgTeamScoreStats_t;

typedef struct {
	qboolean	valid;
	int		damageGiven;
	int		damageReceived;
	int		weaponFrags[WP_NUM_WEAPONS];
	int		weaponAccuracy[WP_NUM_WEAPONS];
} cgClanArenaStats_t;

#define CG_TDMSTAT_FIELD_COUNT	11
#define CG_CTFSTAT_FIELD_COUNT	12

typedef struct {
	qboolean	valid;
	int		values[CG_TDMSTAT_FIELD_COUNT];
} cgTdmStats_t;

typedef struct {
	qboolean	valid;
	int		values[CG_CTFSTAT_FIELD_COUNT];
} cgCtfStats_t;

// HUD scoreboard export used by competitive menu overlays
typedef struct {
	int					clientNum;
	int					score;
	int					ping;
	int					time;
	team_t			team;
	qboolean			spectator;
	qboolean			localPlayer;
} cgHudScoreboardEntry_t;

typedef struct {
	int					count;
	cgHudScoreboardEntry_t	entries[MAX_CLIENTS];
	float				scoreX;
	float				scoreWidth;
	float				pingX;
	float				pingWidth;
	float				timeX;
	float				timeWidth;
	float				nameX;
	float				nameWidth;
	float					scale;
	float					scoreboardX;
	float					scoreboardWidth;
	int					gametype;
	int					variant;
	qboolean			teamGame;
	int					redScore;
	int					blueScore;
	team_t			leadingTeam;
	qboolean			scoresTied;
	char				summary[128];
	qboolean			widescreen;
	qboolean			overtimeVisible;
	qboolean			overtimeConfigured;
	qboolean			overtimeActive;
	int				overtimeCount;
	char				overtimeLabel[32];
	qboolean			suddenDeathConfigured;
	qboolean			suddenDeathActive;
	qboolean			suddenDeathRespawns;
	qboolean			suddenDeathDelayActive;
	int				suddenDeathStart;
	int				suddenDeathTick;
	int				suddenDeathMax;
	int				suddenDeathIncrement;
	qboolean			suddenDeathVisible;
	char				suddenDeathLabel[32];
	int					teamCounts[TEAM_NUM_TEAMS];
} cgHudScoreboard_t;

// each client has an associated clientInfo_t
// that contains media references necessary to present the
// client model and other color coded effects
// this is regenerated each time a client's configstring changes,
// usually as a result of a userinfo (name, model, etc) change
#define	MAX_CUSTOM_SOUNDS	32

typedef struct {
	qboolean		infoValid;

	char			name[MAX_QPATH];
	team_t			team;

	int				botSkill;		// 0 = not bot, 1-5 = bot

	vec3_t			color1;
	vec3_t			color2;
	vec3_t			headColor;
	vec3_t			upperColor;
	vec3_t			lowerColor;
	vec3_t			weaponPrimaryColor;
	vec3_t			weaponSecondaryColor;

	qboolean			headColorForced;
	qboolean			upperColorForced;
	qboolean			lowerColorForced;
	qboolean			weaponColorForced;
	qboolean			modelForced;
	qboolean			headModelForced;
	qboolean			skinForced;

	int				score;			// updated by score servercmds
	int				location;		// location index for team mode
	int				health;			// you only get this info about your teammates
	int				armor;
	int				curWeapon;

	int				handicap;
	int				wins, losses;	// in tourney mode

	int				teamTask;		// task in teamplay (offence/defence)
	qboolean		teamLeader;		// true when this is a team leader
	qboolean		spectateOnly;		// retail duel pure-spectator flag
	int				spectatorQueuePosition;	// retail duel queue position

	int				powerups;		// so can display quad/flag status

	int				medkitUsageTime;
	int				invulnerabilityStartTime;
	int				invulnerabilityStopTime;

	int				breathPuffTime;

	// when clientinfo is changed, the loading of models/skins/sounds
	// can be deferred until you are dead, to prevent hitches in
	// gameplay
	char			modelName[MAX_QPATH];
	char			skinName[MAX_QPATH];
	char			headModelName[MAX_QPATH];
	char			headSkinName[MAX_QPATH];
	char			redTeam[MAX_TEAMNAME];
	char			blueTeam[MAX_TEAMNAME];
	char			country[MAX_COUNTRY_CODE];
	qhandle_t		countryFlagShader;
	qboolean		deferred;

	qboolean		newAnims;		// true if using the new mission pack animations
	qboolean		fixedlegs;		// true if legs yaw is always the same as torso yaw
	qboolean		fixedtorso;		// true if torso never changes yaw

	vec3_t			headOffset;		// move head in icon views
	footstep_t		footsteps;
	gender_t		gender;			// from model

	qhandle_t		legsModel;
	qhandle_t		legsSkin;

	qhandle_t		torsoModel;
	qhandle_t		torsoSkin;

	qhandle_t		headModel;
	qhandle_t		headSkin;

	qhandle_t		modelIcon;

	animation_t		animations[MAX_TOTALANIMATIONS];

	sfxHandle_t		sounds[MAX_CUSTOM_SOUNDS];
} clientInfo_t;


// each WP_* weapon enum has an associated weaponInfo_t
// that contains media references necessary to present the
// weapon and its effects
typedef struct weaponInfo_s {
	qboolean		registered;
	gitem_t			*item;

	qhandle_t		handsModel;			// the hands don't actually draw, they just position the weapon
	qhandle_t		weaponModel;
	qhandle_t		barrelModel;
	qhandle_t		flashModel;

	vec3_t			weaponMidpoint;		// so it will rotate centered instead of by tag

	float			flashDlight;
	vec3_t			flashDlightColor;
	sfxHandle_t		flashSound[4];		// fast firing weapons randomly choose

	qhandle_t		weaponIcon;
	qhandle_t		ammoIcon;

	qhandle_t		ammoModel;

	qhandle_t		missileModel;
	sfxHandle_t		missileSound;
	void			(*missileTrailFunc)( centity_t *, const struct weaponInfo_s *wi );
	float			missileDlight;
	vec3_t			missileDlightColor;
	int				missileRenderfx;

	void			(*ejectBrassFunc)( centity_t * );

	float			trailRadius;
	float			wiTrailTime;

	sfxHandle_t		readySound;
	sfxHandle_t		firingSound;
	qboolean		loopFireSound;
} weaponInfo_t;


// each IT_* item has an associated itemInfo_t
// that constains media references necessary to present the
// item and its effects
typedef struct {
	qboolean		registered;
	qhandle_t		models[MAX_ITEM_MODELS];
	qhandle_t		icon;
} itemInfo_t;


typedef struct {
	int				itemNum;
} powerupInfo_t;


#define MAX_SKULLTRAIL		10

typedef struct {
	vec3_t positions[MAX_SKULLTRAIL];
	int numpositions;
} skulltrail_t;


#define MAX_REWARDSTACK		10
#define MAX_SOUNDBUFFER		20

//======================================================================

// all cg.stepTime, cg.duckTime, cg.landTime, etc are set to cg.time when the action
// occurs, and they will have visible effects for #define STEP_TIME or whatever msec after

#define MAX_PREDICTED_EVENTS	16

typedef struct {
	qboolean	active;
	int		time;
	char		targetName[CG_OBITUARY_NAME_SIZE];
	int		targetColorIndex;
	char		attackerName[CG_OBITUARY_NAME_SIZE];
	int		attackerColorIndex;
	qboolean	hasAttacker;
	qhandle_t	icon;
	int		attacker;
	int		target;
	int		mod;
} cgObituary_t;

#define CG_SPECTATOR_ITEM_PICKUP_COUNT	10

typedef struct {
	int		clientNum;
	int		palette;
	int		itemNum;
	int		remainingTime;
	int		duelLayout;
	int		layoutOrder;
	vec3_t	origin;
} cgSpectatorItemPickup_t;
 
typedef struct {
	int			clientFrame;		// incremented each frame

	int			clientNum;
	
	qboolean	demoPlayback;
	qboolean	levelShot;			// taking a level menu screenshot
	int			deferredPlayerLoading;
	qboolean	loading;			// don't defer players at initial startup
	qboolean	competitiveHudLoaded;	// tracks if Quake Live HUD menus are available
	qboolean	armorTieredEnabled;	// caches cg_armorTiered for HUD scripting
	qboolean	voiceChatIndicatorEnabled;	// caches cg_voiceChatIndicator state
	qboolean	vignetteEnabled;	// caches cg_vignette state
	qboolean	intermissionStarted;	// don't play voice rewards, because game will end shortly
	int			intermissionLetterboxChangeTime;
	int			intermissionLetterboxDuration;
	float		intermissionLetterboxStartHeight;
	float		intermissionLetterboxTargetHeight;

	// there are only one or two snapshot_t that are relevent at a time
	int			latestSnapshotNum;	// the number of snapshots the client system has received
	int			latestSnapshotTime;	// the time from latestSnapshotNum, so we don't need to read the snapshot yet

	snapshot_t	*snap;				// cg.snap->serverTime <= cg.time
	snapshot_t	*nextSnap;			// cg.nextSnap->serverTime > cg.time, or NULL
	snapshot_t	activeSnapshots[2];

	float		frameInterpolation;	// (float)( cg.time - cg.frame->serverTime ) / (cg.nextFrame->serverTime - cg.frame->serverTime)

	qboolean	thisFrameTeleport;
	qboolean	nextFrameTeleport;

	int			frametime;		// cg.time - cg.oldTime

	int			time;			// this is the time value that the client
								// is rendering at.
	int			oldTime;		// time at last frame, used for missile trails and prediction checking

	int			physicsTime;	// either cg.snap->time or cg.nextSnap->time

	int			timelimitWarnings;	// 5 min, 1 min, overtime
	int			fraglimitWarnings;

	qboolean	mapRestart;			// set on a map restart to set back the weapon

	qboolean	renderingThirdPerson;		// during deaths, chasecams, etc

	// prediction state
	qboolean	hyperspace;				// true if prediction has hit a trigger_teleport
	playerState_t	predictedPlayerState;
	centity_t		predictedPlayerEntity;
	qboolean	validPPS;				// clear until the first call to CG_PredictPlayerState
	int			predictedErrorTime;
	vec3_t		predictedError;

	int			eventSequence;
	int			predictableEvents[MAX_PREDICTED_EVENTS];

	float		stepChange;				// for stair up smoothing
	int			stepTime;

	float		duckChange;				// for duck viewheight smoothing
	int			duckTime;

	float		landChange;				// for landing hard
	int			landTime;

	// input state sent to server
	int			weaponSelect;

	// auto rotating items
	vec3_t		autoAngles;
	vec3_t		autoAxis[3];
	vec3_t		autoAnglesFast;
	vec3_t		autoAxisFast[3];

	// view rendering
	refdef_t	refdef;
	vec3_t		refdefViewAngles;		// will be converted to refdef.viewaxis
	cgViewAngleFilter_t	viewFilter;

	// zoom key
	qboolean	zoomed;
	int			zoomTime;
	float		zoomSensitivity;
	qboolean	zoomToggle;
	qboolean	zoomOutOnDeath;
	qboolean	autoHopEnabled;
	qboolean	autoProjectileNudgeEnabled;
	qboolean	projectileNudgeActive;
	float		projectileNudgeAmount;
	float		projectileNudgeOffset;
	qboolean	predictLocalRailshots;
	int			autoActionFlags;
	qboolean	autoActionFired;
	qboolean	autoActionScreenshotQueued;
	qboolean	autoActionStatsQueued;
	int			autoActionScreenshotTime;
	int			autoActionStatsTime;
	int			autoActionDemoIndex;
	int			weaponAccuracies[WP_NUM_WEAPONS];
	qboolean	accRequestActive;
	int			accRequestTime;
	qboolean	deadBodyDarken;
	vec4_t		deadBodyColor;

	// information screen text during loading
	char		infoScreenText[MAX_STRING_CHARS];

	// scoreboard
	int			scoresRequestTime;
	int			numScores;
	int			selectedScore;
	int			teamScores[2];
	score_t		scores[MAX_CLIENTS];
	cgScoreStats_t	scoreStats[MAX_CLIENTS];
	cgTeamScoreStats_t	teamScoreStats;
	cgClanArenaStats_t	clanArenaStats[MAX_CLIENTS];
	cgTdmStats_t	tdmStats[MAX_CLIENTS];
	cgCtfStats_t	ctfStats[MAX_CLIENTS];
	int			clientKeyMask[MAX_CLIENTS];
	qboolean		clientMuted[MAX_CLIENTS];
	qboolean	showScores;
	qboolean	scoreBoardShowing;
	qboolean	scoreboardTimerRunning;
	int			scoreboardTimerStartTime;
	int			scoreboardTimerStopTime;
	int			scoreFadeTime;
	char		killerName[MAX_NAME_LENGTH];
	int			pendingFollowKillerClient;
	int			pendingFollowKillerTime;
	cgObituary_t	obituaries[MAX_OBITUARIES];
	int			obituaryIndex;
	char			spectatorList[MAX_STRING_CHARS];		// list of names
	char			spectatorEntries[MAX_CLIENTS][64];
	int				spectatorLen;												// length of list
	int				spectatorEntryCount;
	float			spectatorWidth;											// width in device units
	int				spectatorTime;											// next time to offset
	int				spectatorPaintX;										// current paint x
	int				spectatorPaintX2;										// current paint x
	int				spectatorOffset;										// current offset from start
	int				spectatorPaintLen; 									// current offset from start
	int				spectatorPrimaryClient;
	int				spectatorSecondaryClient;
	int				spectatorFollowClient;
	int				spectatorClientOrder[MAX_CLIENTS];
	int				spectatorClientCount;
	int				spectatorTargetUpdateTime;
	int				spectatorTrackedClient;
	int				spectatorSlotTrackedTime[2];
	qboolean		spectatorCameraLocked;
	cgSpectatorItemPickup_t	spectatorItemPickups[CG_SPECTATOR_ITEM_PICKUP_COUNT];
	int				spectatorItemPickupCount;
	int				trackedPlayerClientNum;
	int				trackedPlayerExpireTime;
	cgSpectatorTrackType_t	trackedPlayerPriority;

	// skull trails
	skulltrail_t	skulltrails[MAX_CLIENTS];

	// centerprinting
	int			centerPrintTime;
	float			centerPrintScale;
	int			centerPrintY;
	char		centerPrint[1024];
	int			centerPrintLines;

	// low ammo warning state
	int			lowAmmoWarning;		// 1 = low, 2 = empty, 3 = weapon empty w/manual switch
	float		lowAmmoWarningPercentile;
	vec4_t		weaponBarGrenadeColor;

	// kill timers for carnage reward
	int			lastKillTime;

	// crosshair client ID
	int			crosshairClientNum;
	int			crosshairClientTime;
	vec4_t			crosshairColor;
	vec4_t			crosshairHitColor;
	qboolean	crosshairPulseEnabled;
	int			crosshairHitStyle;
	int			crosshairHitTime;

	// powerup active flashing
	int			powerupActive;
	int			powerupTime;

	// attacking player
	int			attackerTime;
	int			voiceTime;
	qboolean		chatHistoryVisible;

	// reward medals
	int			rewardStack;
	int			rewardTime;
	int			rewardCount[MAX_REWARDSTACK];
	qhandle_t	rewardShader[MAX_REWARDSTACK];
	qhandle_t	rewardSound[MAX_REWARDSTACK];

	// sound buffer mainly for announcer sounds
	int			soundBufferIn;
	int			soundBufferOut;
	int			soundTime;
	qhandle_t	soundBuffer[MAX_SOUNDBUFFER];

	// for voice chat buffer
	int			voiceChatTime;
	int			voiceChatBufferIn;
	int			voiceChatBufferOut;

	// warmup countdown
	int			warmup;
	int			warmupCount;

	//==========================

	int			itemPickup;
	int			itemPickupTime;
	int			itemPickupBlendTime;	// the pulse around the crosshair is timed seperately

	int			weaponSelectTime;
	int			weaponAnimation;
	int			weaponAnimationTime;

	// blend blobs
	float		damageTime;
	float		damageX, damageY, damageValue;
	damagePlumPreset_t	damagePlumPreset;
	unsigned int	damagePlumWeaponBits;
	damagePlumColorStyle_t	damagePlumColorStyle;

	// cached screen damage customization
	vec4_t		screenDamageColor;
	vec4_t		screenDamageSelfColor;
	vec4_t		screenDamageTeamColor;
	float		screenDamageAlpha;
	float		screenDamageAlphaTeam;

	// status bar head
	float		headYaw;
	float		headEndPitch;
	float		headEndYaw;
	int			headEndTime;
	float		headStartPitch;
	float		headStartYaw;
	int			headStartTime;

	// view movement
	float		v_dmg_time;
	float		v_dmg_pitch;
	float		v_dmg_roll;
	float		kickScale;
	float		bobScale;
	float		simpleItemsHeightOffset;
	float		simpleItemsRadius;
	float		simpleItemsBob;

	vec3_t		kick_angles;	// weapon kicks
	vec3_t		kick_origin;
	int		projectileNudgeCommandTime;
	int		projectileNudgeMsec;
	vec3_t		projectileNudgeOrigin;

	// temp working variables for player view
	float		bobfracsin;
	int			bobcycle;
	float		xyspeed;
	float		speedometerSample;
	int		speedometerSampleTime;
	int		predictedLocalRailTime;
	int		predictedLocalLightningTime;
	qboolean		predictedLocalRailValid;
	qboolean		predictedLocalLightningValid;
	qboolean		predictedLocalRailHit;
	qboolean		predictedLocalLightningHit;
	vec3_t		predictedLocalRailStart;
	vec3_t		predictedLocalRailEnd;
	vec3_t		predictedLocalLightningStart;
	vec3_t		predictedLocalLightningEnd;
	int     nextOrbitTime;

	//qboolean cameraMode;		// if rendering from a loaded camera


	// development tool
	refEntity_t		testModelEntity;
	char			testModelName[MAX_QPATH];
	qboolean		testGun;

	int				rageQuitTime;
} cg_t;


// all of the model, shader, and sound references that are
// loaded at gamestate time are stored in cgMedia_t
// Other media that can be tied to clients, weapons, or items are
// stored in the clientInfo_t, itemInfo_t, weaponInfo_t, and powerupInfo_t
typedef struct {
	qhandle_t	charsetShader;
	qhandle_t	charsetProp;
	qhandle_t	charsetPropGlow;
	qhandle_t	charsetPropB;
	qhandle_t	whiteShader;
	qhandle_t	loadingBackground;
	qhandle_t	gameTypeBackground;
	qhandle_t	logoBackground;
	qhandle_t	qlLogo;
	qhandle_t	menuSmokeShader;
	qhandle_t	modifiedIcon;

	qhandle_t	redCubeModel;
	qhandle_t	blueCubeModel;
	qhandle_t	redCubeIcon;
	qhandle_t	blueCubeIcon;
	qhandle_t	redFlagModel;
	qhandle_t	blueFlagModel;
	qhandle_t	neutralFlagModel;
	qhandle_t	redFlagShader[3];
	qhandle_t	blueFlagShader[3];
	qhandle_t	flagShader[4];

	qhandle_t	flagPoleModel;
	qhandle_t	flagFlapModel;

	qhandle_t	redFlagFlapSkin;
	qhandle_t	blueFlagFlapSkin;
	qhandle_t	neutralFlagFlapSkin;

	qhandle_t	redFlagBaseModel;
	qhandle_t	blueFlagBaseModel;
	qhandle_t	neutralFlagBaseModel;

	qhandle_t	overloadBaseModel;
	qhandle_t	overloadTargetModel;
	qhandle_t	overloadLightsModel;
	qhandle_t	overloadEnergyModel;

	qhandle_t	harvesterModel;
	qhandle_t	harvesterRedSkin;
	qhandle_t	harvesterBlueSkin;
	qhandle_t	harvesterNeutralModel;

	qhandle_t	domPointModel;
	qhandle_t	domPointSkinRed;
	qhandle_t	domPointSkinBlue;
	qhandle_t	domPointSkinNeutral;
	qhandle_t	domCapShaders[DOM_POINT_STATE_COUNT];
	qhandle_t	domCapDistressShaders[DOM_POINT_STATE_COUNT];
	qhandle_t	domDefShaders[DOM_POINT_STATE_COUNT];
	qhandle_t	domDefDistressShaders[DOM_POINT_STATE_COUNT];

	qhandle_t	armorModel;
	qhandle_t	armorIcon;

	qhandle_t	teamStatusBar;

	qhandle_t	deferShader;

	// gib explosions
	qhandle_t	gibAbdomen;
	qhandle_t	gibArm;
	qhandle_t	gibChest;
	qhandle_t	gibFist;
	qhandle_t	gibFoot;
	qhandle_t	gibForearm;
	qhandle_t	gibIntestine;
	qhandle_t	gibLeg;
	qhandle_t	gibSkull;
	qhandle_t	gibBrain;
	qboolean	haveDlcGibs;

	qhandle_t	smoke2;

	qhandle_t	machinegunBrassModel;
	qhandle_t	shotgunBrassModel;

	qhandle_t	railRingsShader;
	qhandle_t	railCoreShader;

	qhandle_t	lightningShader;
	qhandle_t	lightningStyleShaders[CG_MAX_LIGHTNING_STYLES];
	qhandle_t	grapplingChainShader;

	qhandle_t	friendShader;
	qhandle_t	frozenPlayerShader;

	qhandle_t	balloonShader;
	qhandle_t	connectionShader;

	qhandle_t	selectShader;
	qhandle_t	viewBloodShader;
	qhandle_t	tracerShader;
	qhandle_t	crosshairShader[NUM_CROSSHAIRS];
	qhandle_t	lagometerShader;
	qhandle_t	backTileShader;
	qhandle_t	noammoShader;
	qhandle_t	infiniteAmmoShader;
	qhandle_t	healthBar100;
	qhandle_t	healthBar200;
	qhandle_t	armorBar100;
	qhandle_t	armorBar200;
	qhandle_t	healthTick100;
	qhandle_t	healthTick200;
	qhandle_t	armorTick100;
	qhandle_t	armorTick200;

	qhandle_t	smokePuffShader;
	qhandle_t	smokePuffRageProShader;
	qhandle_t	shotgunSmokePuffShader;
	qhandle_t	plasmaBallShader;
	qhandle_t	waterBubbleShader;
	qhandle_t	bloodTrailShader;
	qhandle_t	bloodSprayShaders[4];
	qhandle_t	nailPuffShader;
	qhandle_t	blueProxMine;
	qhandle_t	iceTrailShader;
	qhandle_t	iceballShader;

	qhandle_t	numberShaders[11];

	qhandle_t	shadowMarkShader;

	qhandle_t	botSkillShaders[5];

	// wall mark shaders
	qhandle_t	wakeMarkShader;
	qhandle_t	bloodMarkShader;
	qhandle_t	bulletMarkShader;
	qhandle_t	burnMarkShader;
	qhandle_t	iceMarkShader;
	qhandle_t	holeMarkShader;
	qhandle_t	energyMarkShader;

	// powerup shaders
	qhandle_t	quadShader;
	qhandle_t	redQuadShader;
	qhandle_t	quadWeaponShader;
	qhandle_t	invisShader;
	qhandle_t	regenShader;
	qhandle_t	battleSuitShader;
	qhandle_t	battleWeaponShader;
	qhandle_t	hastePuffShader;
	qhandle_t	redKamikazeShader;
	qhandle_t	blueKamikazeShader;

	// weapon effect models
	qhandle_t	bulletFlashModel;
	qhandle_t	ringFlashModel;
	qhandle_t	dishFlashModel;
	qhandle_t	lightningExplosionModel;

	// weapon effect shaders
	qhandle_t	railExplosionShader;
	qhandle_t	plasmaExplosionShader;
	qhandle_t	bulletExplosionShader;
	qhandle_t	rocketExplosionShader;
	qhandle_t	grenadeExplosionShader;
	qhandle_t	bfgExplosionShader;
	qhandle_t	bloodExplosionShader;

	// special effects models
	qhandle_t	teleportEffectModel;
	qhandle_t	teleportEffectShader;
	qhandle_t	kamikazeEffectModel;
	qhandle_t	kamikazeShockWave;
	qhandle_t	kamikazeHeadModel;
	qhandle_t	kamikazeHeadTrail;
	qhandle_t	guardPowerupModel;
	qhandle_t	scoutPowerupModel;
	qhandle_t	doublerPowerupModel;
	qhandle_t	ammoRegenPowerupModel;
	qhandle_t	invulnerabilityImpactModel;
	qhandle_t	invulnerabilityJuicedModel;
	qhandle_t	medkitUsageModel;
	qhandle_t	dustPuffShader;
	qhandle_t	heartShader;
	qhandle_t	invulnerabilityPowerupModel;

	// scoreboard headers
	qhandle_t	scoreboardName;
	qhandle_t	scoreboardPing;
	qhandle_t	scoreboardScore;
	qhandle_t	scoreboardTime;
	qhandle_t	scoreboxSpecShader;
	qhandle_t	scoreboxFollowShader;
	qhandle_t	scoreMutedShader;
	qhandle_t	scoreSpeakingShader;
	qhandle_t	inkFadeLeftShader;
	qhandle_t	inkFadeRightShader;

	// medals shown during gameplay
	qhandle_t	medalImpressive;
	qhandle_t	medalExcellent;
	qhandle_t	medalGauntlet;
	qhandle_t	medalDefend;
	qhandle_t	medalAssist;
	qhandle_t	medalCapture;
	qhandle_t	medalAccuracy;
	qhandle_t	medalComboKill;
	qhandle_t	medalMidair;
	qhandle_t	medalPerfect;
	qhandle_t	medalQuadGod;
	qhandle_t	medalRampage;
	qhandle_t	medalRevenge;
	qhandle_t	medalPerforated;
	qhandle_t	medalHeadshot;
	qhandle_t	medalFirstFrag;

	// sounds
	sfxHandle_t	quadSound;
	sfxHandle_t	tracerSound;
	sfxHandle_t	selectSound;
	sfxHandle_t	useNothingSound;
	sfxHandle_t	wearOffSound;
	sfxHandle_t	footsteps[FOOTSTEP_TOTAL][4];
	sfxHandle_t	sfx_lghit1;
	sfxHandle_t	sfx_lghit2;
	sfxHandle_t	sfx_lghit3;
	sfxHandle_t	sfx_ric1;
	sfxHandle_t	sfx_ric2;
	sfxHandle_t	sfx_ric3;
	sfxHandle_t	sfx_railg;
	sfxHandle_t	sfx_rockexp;
	sfxHandle_t	sfx_plasmaexp;
	sfxHandle_t	sfx_proxexp;
	sfxHandle_t	sfx_nghit;
	sfxHandle_t	sfx_nghitflesh;
	sfxHandle_t	sfx_nghitmetal;
	sfxHandle_t	sfx_chghit;
	sfxHandle_t	sfx_chghitflesh;
	sfxHandle_t	sfx_chghitmetal;
	sfxHandle_t	sfx_chgwind;
	sfxHandle_t kamikazeExplodeSound;
	sfxHandle_t kamikazeImplodeSound;
	sfxHandle_t kamikazeFarSound;
	sfxHandle_t useInvulnerabilitySound;
	sfxHandle_t invulnerabilityImpactSound1;
	sfxHandle_t invulnerabilityImpactSound2;
	sfxHandle_t invulnerabilityImpactSound3;
	sfxHandle_t invulnerabilityJuicedSound;
	sfxHandle_t obeliskHitSound1;
	sfxHandle_t obeliskHitSound2;
	sfxHandle_t obeliskHitSound3;
	sfxHandle_t	obeliskRespawnSound;
	sfxHandle_t	winnerSound;
	sfxHandle_t	loserSound;
	sfxHandle_t	youSuckSound;
	sfxHandle_t	gibSound;
	sfxHandle_t	gibBounce1Sound;
	sfxHandle_t	gibBounce2Sound;
	sfxHandle_t	gibBounce3Sound;
	sfxHandle_t	electroGibBounce1Sound;
	sfxHandle_t	electroGibBounce2Sound;
	sfxHandle_t	electroGibBounce3Sound;
	sfxHandle_t	electroGibBounce4Sound;
	sfxHandle_t	electroGibBounce5Sound;
	sfxHandle_t	teleInSound;
	sfxHandle_t	teleOutSound;
	sfxHandle_t	noAmmoSound;
	sfxHandle_t	respawnSound;
	sfxHandle_t talkSound;
	sfxHandle_t landSound;
	sfxHandle_t fallSound;
	sfxHandle_t jumpPadSound;

	cgAnnouncerSoundSet_t announcerSoundSets[ANNOUNCER_PROFILE_COUNT];

	sfxHandle_t oneMinuteSound;
	sfxHandle_t fiveMinuteSound;
	sfxHandle_t suddenDeathSound;
	sfxHandle_t overtimeSound;

	sfxHandle_t threeFragSound;
	sfxHandle_t twoFragSound;
	sfxHandle_t oneFragSound;

	sfxHandle_t hitSound;
	sfxHandle_t hitSoundHighArmor;
	sfxHandle_t hitSoundLowArmor;
	sfxHandle_t hitTeamSound;
	sfxHandle_t impressiveSound;
	sfxHandle_t impressiveSound2;
	sfxHandle_t impressiveSound3;
	sfxHandle_t excellentSound;
	sfxHandle_t deniedSound;
	sfxHandle_t humiliationSound;
	sfxHandle_t assistSound;
	sfxHandle_t defendSound;
	sfxHandle_t firstImpressiveSound;
	sfxHandle_t firstExcellentSound;
	sfxHandle_t firstHumiliationSound;
	sfxHandle_t comboKillSound;
	sfxHandle_t comboKillSound2;
	sfxHandle_t comboKillSound3;
	sfxHandle_t midairSound;
	sfxHandle_t midairSound2;
	sfxHandle_t midairSound3;
	sfxHandle_t accuracySound;
	sfxHandle_t perfectSound;
	sfxHandle_t quadGodSound;
	sfxHandle_t rampageSound;
	sfxHandle_t rampageSound2;
	sfxHandle_t rampageSound3;
	sfxHandle_t revengeSound;
	sfxHandle_t revengeSound2;
	sfxHandle_t revengeSound3;
	sfxHandle_t perforatedSound;
	sfxHandle_t headshotSound;
	sfxHandle_t firstFragSound;
	sfxHandle_t infectedSound;
	sfxHandle_t newHighScoreSound;

	sfxHandle_t takenLeadSound;
	sfxHandle_t tiedLeadSound;
	sfxHandle_t lostLeadSound;

	sfxHandle_t voteNow;
	sfxHandle_t votePassed;
	sfxHandle_t voteFailed;

	sfxHandle_t watrInSound;
	sfxHandle_t watrOutSound;
	sfxHandle_t watrUnSound;

	sfxHandle_t flightSound;
	sfxHandle_t medkitSound;

	sfxHandle_t weaponHoverSound;

	// teamplay sounds
	sfxHandle_t captureAwardSound;
	sfxHandle_t redScoredSound;
	sfxHandle_t blueScoredSound;
	sfxHandle_t redLeadsSound;
	sfxHandle_t blueLeadsSound;
	sfxHandle_t teamsTiedSound;

	sfxHandle_t	captureYourTeamSound;
	sfxHandle_t	captureOpponentSound;
	sfxHandle_t	returnYourTeamSound;
	sfxHandle_t	returnOpponentSound;
	sfxHandle_t	takenYourTeamSound;
	sfxHandle_t	takenOpponentSound;

	sfxHandle_t redFlagReturnedSound;
	sfxHandle_t blueFlagReturnedSound;
	sfxHandle_t neutralFlagReturnedSound;
	sfxHandle_t	enemyTookYourFlagSound;
	sfxHandle_t	enemyTookTheFlagSound;
	sfxHandle_t yourTeamTookEnemyFlagSound;
	sfxHandle_t yourTeamTookTheFlagSound;
	sfxHandle_t	youHaveFlagSound;
	sfxHandle_t yourBaseIsUnderAttackSound;
	sfxHandle_t holyShitSound;
	sfxHandle_t dominationDistressSound;
	sfxHandle_t raceStartBeep;
	sfxHandle_t raceCheckpointBeep;
	sfxHandle_t raceFinishBeep;

	// tournament sounds
	sfxHandle_t	count3Sound;
	sfxHandle_t	count2Sound;
	sfxHandle_t	count1Sound;
	sfxHandle_t	countFightSound;
	sfxHandle_t	countPrepareSound;

	// new stuff
	qhandle_t patrolShader;
	qhandle_t assaultShader;
	qhandle_t campShader;
	qhandle_t followShader;
	qhandle_t defendShader;
	qhandle_t teamLeaderShader;
	qhandle_t retrieveShader;
	qhandle_t escortShader;
	qhandle_t flagShaders[3];
	qhandle_t countryFlagNoneShader;
	qhandle_t	raceStartShader;
	qhandle_t	raceCheckpointShader;
	qhandle_t	raceFinishShader;
	sfxHandle_t	countPrepareTeamSound;

	sfxHandle_t ammoregenSound;
	sfxHandle_t doublerSound;
	sfxHandle_t guardSound;
	sfxHandle_t scoutSound;
	qhandle_t cursor;
	qhandle_t selectCursor;
	qhandle_t sizeCursor;

	sfxHandle_t	regenSound;
	sfxHandle_t	protectSound;
	sfxHandle_t	n_healthSound;
	sfxHandle_t	hgrenb1aSound;
	sfxHandle_t	hgrenb2aSound;
	sfxHandle_t	wstbimplSound;
	sfxHandle_t	wstbimpmSound;
	sfxHandle_t	wstbimpdSound;
	sfxHandle_t	wstbactvSound;

	qhandle_t	waterIcon;
	qhandle_t	slimeIcon;
	qhandle_t	lavaIcon;
	qhandle_t	crushIcon;
	qhandle_t	telefragIcon;
	qhandle_t	fallingIcon;
	qhandle_t	suicideIcon;
	qhandle_t	kamikazeIcon;
	qhandle_t	juicedIcon;

} cgMedia_t;


// The client game static (cgs) structure hold everything
// loaded or calculated from the gamestate.  It will NOT
// be cleared when a tournement restart is done, allowing
// all clients to begin playing instantly
typedef struct {
	gameState_t		gameState;			// gamestate from server
	glconfig_t		glconfig;			// rendering configuration
	float			screenXScale;		// derived from glconfig
	float			screenYScale;
	float			screenXBias;

	int				serverCommandSequence;	// reliable command stream counter
	int				processedSnapshotNum;// the number of snapshots cgame has requested

	qboolean		localServer;		// detected on startup by checking sv_running

	// parsed from serverinfo
	gametype_t		gametype;
	int				dmflags;
	int				teamflags;
	int				fraglimit;
	int				capturelimit;
	int				timelimit;
	int				voteFlags;
	int				maxclients;
	int				playerCountTeamSize;
	char			mapname[MAX_QPATH];
	char			loadout[MAX_INFO_VALUE];
	qboolean		playerCylindersEnabled;
	char			redTeam[MAX_QPATH];
	char			blueTeam[MAX_QPATH];
	char			redTeamName[MAX_TEAMNAME];
	char			blueTeamName[MAX_TEAMNAME];
	char			playermodelOverride[MAX_QPATH];
	char			playerheadmodelOverride[MAX_QPATH];
	qboolean		allowCustomHeadmodels;
	float			playerHeadScale;
	float			playerHeadScaleOffset;
	float			playerModelScale;

	int				voteTime;
	int				voteYes;
	int				voteNo;
	qboolean		voteModified;			// beep whenever changed
	char			voteString[MAX_STRING_TOKENS];

	int				teamVoteTime[2];
	int				teamVoteYes[2];
	int				teamVoteNo[2];
	qboolean		teamVoteModified[2];	// beep whenever changed
	char			teamVoteString[2][MAX_STRING_TOKENS];

	int				levelStartTime;

	int				scores1, scores2;		// from configstrings
	int				redflag, blueflag;		// flag status from configstrings
	int				flagStatus;

	qboolean	matchOvertimeActive;
	int		matchOvertimeStartTime;
	int		matchOvertimeEndTime;
	int		matchOvertimeCount;
	qboolean	matchSuddenDeathActive;
	qboolean	matchTimeoutActive;
	int		matchTimeoutTeam;
	int		matchTimeoutExpireTime;
	int		matchTimeoutOwner;
	int		matchTimeoutRemaining[TEAM_NUM_TEAMS];
	int		matchRoundTransitionTime;
	int		matchRoundNumber;
	int		matchRoundTurn;
	int		matchRoundState;
	int		matchTeamCount[TEAM_NUM_TEAMS];
	int		matchTeamRespawnRatio[TEAM_NUM_TEAMS];
	qboolean	matchAutoShuffleArmed;
	int		matchAutoShuffleSecondsRemaining;
	int		matchTimeoutLengthSeconds;
	int		matchTimeoutCountPerTeam;
	int		matchOvertimeLengthSeconds;
	qboolean	matchSuddenDeathRespawnsEnabled;
	int		matchSuddenDeathStartSeconds;
	int		matchSuddenDeathTickSeconds;
	int		matchSuddenDeathMaxSeconds;
	int		matchSuddenDeathIncrementSeconds;
	qboolean	matchSuddenDeathPrintAnnouncements;
	qboolean	matchSuddenDeathSpawnDelayActive;
	int		matchReadyUpDeadline;
	int		matchWarmupReadyPercent;
	int		matchWarmupReadyCount;
	int		matchWarmupReadyEligible;
	char		factoryTitle[MAX_STRING_CHARS];
	unsigned int	factoryFlags;
	unsigned long long	customSettingsMask;
	qboolean	serverSettingsArmorTiered;
	int		serverSettingsQuadFactor;
	int		serverSettingsGravity;
	char		factorySpawnHints[MAX_STRING_CHARS];
	qboolean	itemTimersEnabled;
	int		itemTimerHeight;
	qboolean	forceSmallScoreboardMessage;
	qboolean	forceHudHints;
	qboolean	forceDmgThroughSurface;
	char		forcedAtmosphere[MAX_QPATH];
	char		freezeTipObjective[MAX_STRING_CHARS];
	char		freezeTipThaw[MAX_STRING_CHARS];
	char		freezeTipFreeze[MAX_STRING_CHARS];
	char		freezeTipShoot[MAX_STRING_CHARS];
	char		freezeTipSummary[MAX_STRING_CHARS];

	qboolean  newHud;

	int		racePointCount;
	int		raceLeaderSplitCount;
	cgRacePointInfo_t	racePoints[MAX_RACE_POINTS];
	int		raceLeaderSplits[MAX_RACE_POINTS];

	cgRaceClientProgress_t	raceProgress[MAX_CLIENTS];
	cgRaceClientStatus_t	raceStatus[MAX_CLIENTS];
	int		raceStatusSequence;
	int		raceLeaderClientNum;

	//
	// locally derived information from gamestate
	//
	qhandle_t		gameModels[MAX_MODELS];
	sfxHandle_t		gameSounds[MAX_SOUNDS];

	int				numInlineModels;
	qhandle_t		inlineDrawModel[MAX_MODELS];
	vec3_t			inlineModelMidpoints[MAX_MODELS];

	clientInfo_t	clientinfo[MAX_CLIENTS];

	// teamchat width is *3 because of embedded color codes
	char			teamChatMsgs[TEAMCHAT_HEIGHT][TEAMCHAT_WIDTH*3+1];
	int				teamChatMsgTimes[TEAMCHAT_HEIGHT];
	int				teamChatPos;
	int				teamLastChatPos;

	int cursorX;
	int cursorY;
	cgameEvent_t eventHandling;
	qboolean mouseCaptured;
	qboolean sizingHud;
	void *capturedItem;
	qhandle_t activeCursor;

	// orders
	int currentOrder;
	qboolean orderPending;
	int orderTime;
	int currentVoiceClient;
	int acceptOrderTime;
	int acceptTask;
	int acceptLeader;
	char acceptVoice[MAX_NAME_LENGTH];

	// media
	cgMedia_t		media;

	cgAnnouncerProfile_t	announcerProfile;

} cgs_t;

//==============================================================================

extern	cgs_t			cgs;
extern	cg_t			cg;
extern	centity_t		cg_entities[MAX_GENTITIES];
extern	weaponInfo_t	cg_weapons[MAX_WEAPONS];
extern	itemInfo_t		cg_items[MAX_ITEMS];
extern	pmove_settings_t		cg_pmoveSettings;
extern	markPoly_t		cg_markPolys[MAX_MARK_POLYS];

extern	vmCvar_t		cg_armorTiered;
extern	vmCvar_t		cg_addMarks;
extern	vmCvar_t		cg_allowTaunt;
extern	vmCvar_t		cg_noTaunt;
extern	vmCvar_t		cg_animSpeed;
extern	vmCvar_t		cg_announcer;
extern	vmCvar_t		cg_announcerRewardsVO;
extern	vmCvar_t		cg_autoAction;
extern	vmCvar_t		cg_autoHop;
extern	vmCvar_t		cg_autoswitch;
extern	vmCvar_t		cg_autoProjectileNudge;
extern	vmCvar_t		cg_bigFont;
extern	vmCvar_t		cg_blood;
extern	vmCvar_t		cg_blueTeamName;
extern	vmCvar_t		cg_bob;
extern	vmCvar_t		cg_bobup;
extern	vmCvar_t		cg_bobpitch;
extern	vmCvar_t		cg_bobroll;
extern	vmCvar_t		cg_runpitch;
extern	vmCvar_t		cg_runroll;
extern	vmCvar_t		cg_brassTime;
extern	vmCvar_t		cg_buildScript;
extern	vmCvar_t		cg_cameraMode;
extern	vmCvar_t		cg_cameraOrbit;
extern	vmCvar_t		cg_cameraOrbitDelay;
extern	vmCvar_t		cg_cameraSmartMode;
extern	vmCvar_t		cg_cameraThirdPersonSmartMode;
extern	vmCvar_t		cg_centertime;
extern	vmCvar_t		cg_chatbeep;
extern	vmCvar_t		cg_chatHistoryLength;
extern	vmCvar_t		cg_playVoiceChats;
extern	vmCvar_t		cg_showVoiceText;
extern	vmCvar_t		cg_crosshairBrightness;
extern	vmCvar_t		cg_crosshairColor;
extern	vmCvar_t		cg_crosshairHealth;
extern	vmCvar_t		cg_crosshairHitColor;
extern	int			cg_crosshairHitFeedbackTime;
extern	int			cg_crosshairHitFeedbackValue;
extern	vmCvar_t		cg_crosshairHitStyle;
extern	vmCvar_t		cg_crosshairHitTime;
extern	vmCvar_t		cg_crosshairPulse;
extern	vmCvar_t		cg_crosshairSize;
extern	vmCvar_t		cg_crosshairX;
extern	vmCvar_t		cg_crosshairY;
extern	vmCvar_t		cg_currentSelectedPlayer;
extern	vmCvar_t		cg_currentSelectedPlayerName;
extern	vmCvar_t		cg_damagePlum;
extern	vmCvar_t		cg_damagePlumColorStyle;
extern	vmCvar_t		cg_deadBodyColor;
extern	vmCvar_t		cg_deadBodyDarken;
extern	vmCvar_t		cg_debugAnim;
extern	vmCvar_t		cg_debugEvents;
extern	vmCvar_t		cg_debugPosition;
extern	vmCvar_t		cg_debugOwnerdrawStats;
extern	vmCvar_t		cg_deferPlayers;
extern	vmCvar_t		cg_disableLoadout_g;
extern	vmCvar_t		cg_disableLoadout_mg;
extern	vmCvar_t		cg_disableLoadout_sg;
extern	vmCvar_t		cg_disableLoadout_gl;
extern	vmCvar_t		cg_disableLoadout_rl;
extern	vmCvar_t		cg_disableLoadout_lg;
extern	vmCvar_t		cg_disableLoadout_rg;
extern	vmCvar_t		cg_disableLoadout_pg;
extern	vmCvar_t		cg_disableLoadout_bfg;
extern	vmCvar_t		cg_disableLoadout_gh;
extern	vmCvar_t		cg_disableLoadout_ng;
extern	vmCvar_t		cg_disableLoadout_pl;
extern	vmCvar_t		cg_disableLoadout_cg;
extern	vmCvar_t		cg_disableLoadout_hmg;
extern	vmCvar_t		cg_draw2D;
extern	vmCvar_t		cg_draw3dIcons;
extern	vmCvar_t		cg_drawAmmoWarning;
extern	vmCvar_t		cg_drawAttacker;
extern	vmCvar_t		cg_drawCrosshair;
extern	vmCvar_t		cg_drawCrosshairTeamHealth;
extern	vmCvar_t		cg_drawCrosshairTeamHealthSize;
extern	vmCvar_t		cg_drawDeadFriendTime;
extern	vmCvar_t		cg_drawDemoHUD;
extern	vmCvar_t		cg_drawFPS;
extern	vmCvar_t		cg_drawFragMessages;
extern	vmCvar_t		cg_drawFullWeaponBar;
extern	vmCvar_t		cg_drawGun;
extern	vmCvar_t		cg_drawHitFriendTime;
extern	vmCvar_t		cg_drawIcons;
extern	vmCvar_t		cg_drawInputCmds;
extern	vmCvar_t		cg_drawInputCmdsSize;
extern	vmCvar_t		cg_drawInputCmdsX;
extern	vmCvar_t		cg_drawInputCmdsY;
extern	vmCvar_t		cg_drawItemPickups;
extern	vmCvar_t		cg_drawPregameMessages;
extern	vmCvar_t		cg_drawProfileImages;
extern	vmCvar_t		cg_drawCheckpointRemaining;
extern	vmCvar_t		cg_drawRewards;
extern	vmCvar_t		cg_drawRewardsRowSize;
extern	vmCvar_t		cg_drawSnapshot;
extern	vmCvar_t		cg_drawTimer;
extern	vmCvar_t		cg_drawSpecMessages;
extern	vmCvar_t		cg_drawSprites;
extern	vmCvar_t		cg_drawSpriteSelf;
extern	vmCvar_t		cg_drawStatus;
extern	vmCvar_t		cg_drawTeamOverlay;
extern	vmCvar_t		cg_drawTeamOverlayOpacity;
extern	vmCvar_t		cg_drawTeamOverlaySize;
extern	vmCvar_t		cg_drawTeamOverlayX;
extern	vmCvar_t		cg_drawTeamOverlayY;
extern	vmCvar_t		cg_teamOverlayUserinfo;
extern	vmCvar_t		cg_drawTieredArmorAvailability;
extern	vmCvar_t		cg_enableDust;
extern	vmCvar_t		cg_enableBreath;
extern	vmCvar_t		cg_drawCrosshairNames;
extern	vmCvar_t		cg_enemyCrosshairNames;
extern	vmCvar_t		cg_enemyCrosshairNamesOpacity;
extern	vmCvar_t		cg_enemyColors;
extern	vmCvar_t		cg_enemyHeadColor;
extern	vmCvar_t		cg_enemyLowerColor;
extern	vmCvar_t		cg_enemyUpperColor;
extern	vmCvar_t		cg_errorDecay;
extern	vmCvar_t		cg_filter_angles;
extern	vmCvar_t		cg_followKiller;
extern	vmCvar_t		cg_followPowerup;
extern	vmCvar_t		cg_footsteps;
extern	vmCvar_t		cg_forceModel;
extern	vmCvar_t		cg_forceEnemyModel;
extern	vmCvar_t		cg_enemyModel;
extern	vmCvar_t		cg_forceEnemySkin;
extern	vmCvar_t		cg_forceEnemyWeaponColor;
extern	vmCvar_t		cg_forceTeamModel;
extern	vmCvar_t		cg_teamModel;
extern	vmCvar_t		cg_forceTeamSkin;
extern	vmCvar_t		cg_forceTeamWeaponColor;
extern	vmCvar_t		cg_fov;
extern	vmCvar_t		cg_gameInfo1;
extern	vmCvar_t		cg_gameInfo2;
extern	vmCvar_t		cg_gameInfo3;
extern	vmCvar_t		cg_gameInfo4;
extern	vmCvar_t		cg_gameInfo5;
extern	vmCvar_t		cg_gameInfo6;
extern	vmCvar_t		cg_gametype;
extern	vmCvar_t		cg_gun_x;
extern	vmCvar_t		cg_gun_y;
extern	vmCvar_t		cg_gun_z;
extern	vmCvar_t		cg_gun_frame;
extern	vmCvar_t		cg_hudFiles;
extern	vmCvar_t		cg_ignoreMouseInput;
extern	vmCvar_t		cg_itemTimers;
extern	vmCvar_t		cg_kickScale;
extern	vmCvar_t		cg_lagometer;
extern	vmCvar_t		cg_lastmsg;
extern	vmCvar_t		cg_levelTimerDirection;
extern	vmCvar_t		cg_lightningImpact;
extern	vmCvar_t		cg_lightningImpactCap;
extern	vmCvar_t		cg_lightningStyle;
extern	vmCvar_t		cg_loadout;
extern	vmCvar_t		cg_lowAmmoWarningPercentile;
extern	vmCvar_t		cg_lowAmmoWeaponBarWarning;
extern	vmCvar_t		cg_muzzleFlash;
extern	vmCvar_t		cg_noPlayerAnims;
extern	vmCvar_t		cg_nopredict;
extern	vmCvar_t		cg_synchronousClients;
extern	vmCvar_t		cg_obeliskRespawnDelay;
extern	vmCvar_t		cg_obituaryRowSize;
extern	vmCvar_t		cg_overheadNamesWidth;
extern	vmCvar_t		cg_paused;
extern	vmCvar_t		cg_preferredStartingWeapons;
extern	vmCvar_t		cg_oldPlasma;
extern	vmCvar_t		cg_playerCylinders;
extern	vmCvar_t		cg_smoothClients;
extern	vmCvar_t		pmove_fixed;
extern	vmCvar_t		pmove_msec;
//extern	vmCvar_t		cg_pmove_fixed;
extern	vmCvar_t		cg_predictItems;
extern	vmCvar_t		cg_predictLocalRailshots;
extern	vmCvar_t		cg_projectileNudge;
extern	vmCvar_t		cg_noProjectileTrail;
extern	vmCvar_t		cg_raceBeep;
extern	vmCvar_t		cg_oldRail;
extern	vmCvar_t		cg_railTrailTime;
extern	vmCvar_t		cg_recordSPDemo;
extern	vmCvar_t		cg_recordSPDemoName;
extern	vmCvar_t		cg_redTeamName;
extern	vmCvar_t		cg_oldRocket;
extern	vmCvar_t		cg_scorePlum;
extern	vmCvar_t		cg_screenDamage;
extern	vmCvar_t		cg_screenDamage_Self;
extern	vmCvar_t		cg_screenDamage_Team;
extern	vmCvar_t		cg_screenDamageAlpha;
extern	vmCvar_t		cg_screenDamageAlpha_Team;
extern	vmCvar_t		cg_selfOnTeamOverlay;
extern	vmCvar_t		cg_shadows;
extern	vmCvar_t		cg_showmiss;
extern	vmCvar_t		cg_simpleItems;
extern	vmCvar_t		cg_simpleItemsBob;
extern	vmCvar_t		cg_simpleItemsHeightOffset;
extern	vmCvar_t		cg_simpleItemsRadius;
extern	vmCvar_t		cg_singlePlayer;
extern	vmCvar_t		cg_singlePlayerActive;
extern	vmCvar_t		cg_smallFont;
extern	vmCvar_t		cg_spectating;
extern	vmCvar_t		cg_specItemTimers;
extern	vmCvar_t		cg_specItemTimersSize;
extern	vmCvar_t		cg_specItemTimersX;
extern	vmCvar_t		cg_specItemTimersY;
extern	vmCvar_t		cg_specNames;
extern	vmCvar_t		cg_specTeamVitals;
extern	vmCvar_t		cg_specTeamVitalsHealthColor;
extern	vmCvar_t		cg_speedometer;
extern	vmCvar_t		cg_stats;
extern	vmCvar_t		cg_stereoSeparation;
extern	vmCvar_t		cg_swingSpeed;
extern	vmCvar_t		cg_switchOnEmpty;
extern	vmCvar_t		cg_switchToEmpty;
extern	vmCvar_t		cg_teamChatBeep;
extern	vmCvar_t		cg_teamChatHeight;
extern	vmCvar_t		cg_teamChatsOnly;
extern	vmCvar_t		cg_teamChatTime;
extern	vmCvar_t		cg_teamColors;
extern	vmCvar_t		cg_teamHeadColor;
extern	vmCvar_t		cg_teamLowerColor;
extern	vmCvar_t		cg_teamUpperColor;
extern	vmCvar_t		cg_teammateCrosshairNames;
extern	vmCvar_t		cg_teammateCrosshairNamesOpacity;
extern	vmCvar_t		cg_drawFriend;
extern	vmCvar_t		cg_teammateNames;
extern	vmCvar_t		cg_teammatePOIs;
extern	vmCvar_t		cg_teammatePOIsMaxWidth;
extern	vmCvar_t		cg_teammatePOIsMinWidth;
extern	vmCvar_t		cg_thirdPerson;
extern	vmCvar_t		cg_thirdPersonAngle;
extern	vmCvar_t		cg_thirdPersonPitch;
extern	vmCvar_t		cg_thirdPersonRange;
extern	vmCvar_t		cg_timescale;
extern	vmCvar_t		cg_timescaleFadeEnd;
extern	vmCvar_t		cg_timescaleFadeSpeed;
extern	vmCvar_t		cg_tracerChance;
extern	vmCvar_t		cg_tracerLength;
extern	vmCvar_t		cg_tracerWidth;
extern	vmCvar_t		cg_trackPlayer;
extern	vmCvar_t		cg_trueLightning;
extern	vmCvar_t		cg_trueShotgun;
extern	vmCvar_t		cg_useItemMessage;
extern	vmCvar_t		cg_useItemWarning;
extern	vmCvar_t		cg_viewsize;
extern	vmCvar_t		cg_vignette;
extern	vmCvar_t		cg_voiceChatIndicator;
extern	vmCvar_t		cg_waterWarp;
extern	vmCvar_t		cg_weaponBar;
extern	vmCvar_t		cg_weaponColor_grenade;
extern	vmCvar_t		cg_weaponConfig;
extern	vmCvar_t		cg_weaponConfig_g;
extern	vmCvar_t		cg_weaponConfig_mg;
extern	vmCvar_t		cg_weaponConfig_sg;
extern	vmCvar_t		cg_weaponConfig_gl;
extern	vmCvar_t		cg_weaponConfig_rl;
extern	vmCvar_t		cg_weaponConfig_lg;
extern	vmCvar_t		cg_weaponConfig_rg;
extern	vmCvar_t		cg_weaponConfig_pg;
extern	vmCvar_t		cg_weaponConfig_bfg;
extern	vmCvar_t		cg_weaponConfig_gh;
extern	vmCvar_t		cg_weaponConfig_ng;
extern	vmCvar_t		cg_weaponConfig_pl;
extern	vmCvar_t		cg_weaponConfig_cg;
extern	vmCvar_t		cg_weaponConfig_hmg;
extern	vmCvar_t		cg_weaponPrimary;
extern	vmCvar_t		cg_weaponPrimaryQueued;
extern	vmCvar_t		cg_zoomFov;
extern	vmCvar_t		cg_zoomOutOnDeath;
extern	vmCvar_t		cg_zoomScaling;
extern	vmCvar_t		cg_zoomSensitivity;
extern	vmCvar_t		cg_zoomToggle;
// cg_main.c
//
const char *CG_ConfigString( int index );
const char *CG_Argv( int arg );

void QDECL CG_Printf( const char *msg, ... );
void QDECL CG_Error( const char *msg, ... );

void CG_StartMusic( void );

void CG_UpdateCvars( void );

int CG_CrosshairPlayer( void );
int CG_LastAttacker( void );
int CG_GetChatHistoryLength( void );
qboolean CG_ShouldDisplayVoiceIndicator( void );
void CG_InitBrowserRuntime( void );
void CG_ResetBrowserOverlayState( void );
void CG_SetBrowserFeederSelection( void *overlay, int feeder, int index );
void CG_LoadMenus(const char *menuFile);
void CG_LoadHudMenu( void );
qhandle_t CG_RegisterCountryFlag( const char *countryCode );
void CG_KeyEvent(int key, qboolean down);
void CG_MouseEvent(int x, int y);
void CG_EventHandling(int type);
void CG_RankRunFrame( void );
void CG_SetScoreSelection(void *menu);
score_t *CG_GetSelectedScore();
void CG_BuildSpectatorString();


//
// cg_view.c
//
void CG_TestModel_f (void);
void CG_TestGun_f (void);
void CG_TestModelNextFrame_f (void);
void CG_TestModelPrevFrame_f (void);
void CG_TestModelNextSkin_f (void);
void CG_TestModelPrevSkin_f (void);
void CG_ZoomDown_f( void );
void CG_ZoomUp_f( void );
void CG_AddBufferedSound( sfxHandle_t sfx);
void CG_ClearBufferedAnnouncements( void );

void CG_DrawActiveFrame( int serverTime, stereoFrame_t stereoView, qboolean demoPlayback );


//
// cg_drawtools.c
//
void CG_AdjustFrom640( float *x, float *y, float *w, float *h );
void CG_SetAdjustFrom640Mode( int widescreen );
void CG_FillRect( float x, float y, float width, float height, const float *color );
void CG_DrawPic( float x, float y, float width, float height, qhandle_t hShader );
void CG_DrawString( float x, float y, const char *string, 
				   float charWidth, float charHeight, const float *modulate );


void CG_DrawStringExt( int x, int y, const char *string, const float *setColor, 
		qboolean forceColor, qboolean shadow, int charWidth, int charHeight, int maxChars );
void CG_DrawBigString( int x, int y, const char *s, float alpha );
void CG_DrawBigStringColor( int x, int y, const char *s, vec4_t color );
void CG_DrawSmallString( int x, int y, const char *s, float alpha );
void CG_DrawSmallStringColor( int x, int y, const char *s, vec4_t color );

int CG_DrawStrlen( const char *str );

float	*CG_FadeColor( int startMsec, int totalMsec );
float *CG_TeamColor( int team );
void CG_TileClear( void );
void CG_ColorForHealth( vec4_t hcolor );
void CG_GetColorForHealth( int health, int armor, vec4_t hcolor );

void UI_DrawProportionalString( int x, int y, const char* str, int style, vec4_t color );
void CG_DrawRect( float x, float y, float width, float height, float size, const float *color );
void CG_DrawSides(float x, float y, float w, float h, float size);
void CG_DrawTopBottom(float x, float y, float w, float h, float size);


//
// cg_draw.c, cg_newDraw.c
//
extern	int sortedTeamPlayers[TEAM_MAXOVERLAY];
extern	int	numSortedTeamPlayers;
extern	int drawTeamOverlayModificationCount;
extern  char systemChat[256];
extern  char teamChat1[256];
extern  char teamChat2[256];

void CG_RaceResetState( void );
void CG_ParseRaceInfoString( const char *infoString );
void CG_ParseRaceStatusString( const char *statusString );
void CG_RacePlayCue( cgRaceCue_t cue );

void CG_AddLagometerFrameInfo( void );
void CG_AddLagometerSnapshotInfo( snapshot_t *snap );
void CG_CenterPrint( const char *str, int y, float scale );
void CG_DrawHead( float x, float y, float w, float h, int clientNum, vec3_t headAngles );
void CG_DrawActive( stereoFrame_t stereoView );
void CG_DrawFlagModel( float x, float y, float w, float h, int team, qboolean force2D );
qhandle_t CG_GetObituaryIcon( int mod );
void CG_ObituaryColorForIndex( int colorIndex, float alpha, vec4_t color );
void CG_DrawTeamBackground( int x, int y, int w, int h, float alpha, int team );
void CG_OwnerDraw(float x, float y, float w, float h, float text_x, float text_y, int ownerDraw, int ownerDrawFlags, int align, float special, float scale, vec4_t color, qhandle_t shader, int textStyle);
void CG_Text_Paint(float x, float y, float scale, vec4_t color, const char *text, float adjust, int limit, int style);
int CG_Text_Width(const char *text, float scale, int limit);
int CG_Text_Height(const char *text, float scale, int limit);
void CG_SelectPrevPlayer();
void CG_SelectNextPlayer();
void CG_SpectatorFollowCycle(int dir);
void CG_SpectatorTrackEvent( int clientNum, cgSpectatorTrackType_t trackType );
void CG_UpdateSpectatorTracking( void );
void CG_RecordSpectatorItemPickup( const entityState_t *es );
void CG_ClearSpectatorItemPickups( void );
void CG_UpdateSpectatorItemPickups( void );
qboolean CG_IsSpectatorCamera( void );
qboolean CG_SpectatorFollowRequest( int clientNum );
void CG_StopSpectatorFollow( void );
void CG_SetSpectatorCameraLock( qboolean locked );
void *CG_SetClientSpeakingState( int clientNum, int speaking );
float CG_GetValue(int ownerDraw);
qboolean CG_OwnerDrawVisible(int flags);
void CG_RunMenuScript(char **args);
void CG_ShowResponseHead();
void CG_SetPrintString(int type, const char *p);
void CG_InitTeamChat();
void CG_PushPrintString( const char *text, int type, int holdTime );
void CG_GetTeamColor(vec4_t *color);
void CG_GetColorForIndex( int index, vec4_t color );
int CG_ColorCharToIndex( char ch );
const char *CG_GetTeamName( team_t team );
const char *CG_GetGameStatusText();
const char *CG_GetKillerText();
const char *CG_GetRaceStatusText( void );
const char *CG_GetRaceTimesPrimaryText( void );
const char *CG_GetRaceTimesSecondaryText( void );
void CG_Draw3DModel( float x, float y, float w, float h, qhandle_t model, qhandle_t skin, vec3_t origin, vec3_t angles );
void CG_Text_PaintChar(float x, float y, float width, float height, float scale, float s, float t, float s2, float t2, qhandle_t hShader);
void CG_CheckOrderPending();
const char *CG_GameTypeString();
void CG_RegisterGameTypeIcons( void );
qboolean CG_YourTeamHasFlag();
qboolean CG_OtherTeamHasFlag();
qhandle_t CG_StatusHandle(int task);
qboolean CG_ShouldDrawAccOverlay( void );

/*
=============
CG_DrawNewTeamInfo

Renders the teammate/status list for the new HUD ownerdraws.
=============
*/
void CG_DrawNewTeamInfo(rectDef_t *rect, float text_x, float text_y, float scale, vec4_t color, qhandle_t shader);

/*
=============
CG_DrawTeamSpectators

Displays the primary and secondary spectator targets on the new HUD.
=============
*/
void CG_DrawTeamSpectators(rectDef_t *rect, float scale, vec4_t color, qhandle_t shader);

/*
=============
CG_DrawMedal

Draws the medal counter for a specific ownerdraw on the new HUD.
=============
*/
void CG_DrawMedal(int ownerDraw, rectDef_t *rect, float scale, vec4_t color, qhandle_t shader);



//
// cg_player.c
//
void CG_Player( centity_t *cent );
void CG_ResetPlayerEntity( centity_t *cent );
void CG_AddRefEntityWithPowerups( refEntity_t *ent, entityState_t *state, int team );
void CG_NewClientInfo( int clientNum );
void CG_QueueClientInfoContextRefresh( void );
void CG_ApplyModelOverrides( void );
void CG_RefreshClientHeadOffsets( void );
sfxHandle_t	CG_CustomSound( int clientNum, const char *soundName );

//
// cg_predict.c
//
void CG_BuildSolidList( void );
int	CG_PointContents( const vec3_t point, int passEntityNum );
void CG_Trace( trace_t *result, const vec3_t start, const vec3_t mins, const vec3_t maxs, const vec3_t end, 
					 int skipNumber, int mask );
void CG_PredictPlayerState( void );
void CG_LoadDeferredPlayers( void );


//
// cg_events.c
//
void CG_CheckEvents( centity_t *cent );
const char	*CG_PlaceString( int rank );
int CG_GetOvertimeCount( void );
void CG_EntityEvent( centity_t *cent, vec3_t position );
void CG_PainEvent( centity_t *cent, int health );
void CG_PruneObituaryFeed( void );

qboolean CG_DamagePlumsEnabled( void );
qboolean CG_ShouldRenderDamagePlumForWeapon( weapon_t weapon );
damagePlumColorStyle_t CG_GetDamagePlumColorStyle( void );
int CG_StartingWeaponIndexFromToken( const char *value );


//
// cg_ents.c
//
void CG_SetEntitySoundPosition( centity_t *cent );
void CG_AddPacketEntities( void );
void CG_Beam( centity_t *cent );
void CG_AdjustPositionForMover( const vec3_t in, int moverNum, int fromTime, int toTime, vec3_t out );

void CG_PositionEntityOnTag( refEntity_t *entity, const refEntity_t *parent, 
							qhandle_t parentModel, char *tagName );
void CG_PositionRotatedEntityOnTag( refEntity_t *entity, const refEntity_t *parent, 
							qhandle_t parentModel, char *tagName );



//
// cg_weapons.c
//
void CG_NextWeapon_f( void );
void CG_PrevWeapon_f( void );
void CG_Weapon_f( void );
void CG_SetWeaponSelect( int weapon );

void CG_RegisterWeapon( int weaponNum );
void CG_RegisterItemVisuals( int itemNum );

void CG_FireWeapon( centity_t *cent );
void CG_MissileHitWall( int weapon, int clientNum, vec3_t origin, vec3_t dir, impactSound_t soundType );
void CG_MissileHitPlayer( int weapon, vec3_t origin, vec3_t dir, int entityNum );
void CG_ShotgunFire( entityState_t *es );
void CG_Bullet( vec3_t origin, int sourceEntityNum, vec3_t normal, qboolean flesh, int fleshEntityNum );

void CG_RailTrail( clientInfo_t *ci, vec3_t start, vec3_t end );
void CG_GrappleTrail( centity_t *ent, const weaponInfo_t *wi );
void CG_AddViewWeapon (playerState_t *ps);
void CG_AddPlayerWeapon( refEntity_t *parent, playerState_t *ps, centity_t *cent, int team );
void CG_DrawWeaponSelect( void );
qboolean CG_BuildPredictedRailForPlayerState( const playerState_t *ps, int clientNum,
	vec3_t start, vec3_t end, vec3_t impactDir, qboolean *addImpact );
qboolean CG_BuildPredictedBeamForPlayerState( const playerState_t *ps, int clientNum, weapon_t weapon,
	vec3_t start, vec3_t end, qboolean *hitWorld );

void CG_OutOfAmmoChange( void );	// should this be in pmove?

//
// cg_marks.c
//
void	CG_InitMarkPolys( void );
void	CG_AddMarks( void );
void	CG_ImpactMark( qhandle_t markShader, 
				    const vec3_t origin, const vec3_t dir, 
					float orientation, 
				    float r, float g, float b, float a, 
					qboolean alphaFade, 
					float radius, qboolean temporary );

//
// cg_localents.c
//
void	CG_InitLocalEntities( void );
localEntity_t	*CG_AllocLocalEntity( void );
void	CG_AddLocalEntities( void );

//
// cg_effects.c
//
extern qhandle_t cg_deathEffectShader;
extern qhandle_t cg_gibSphereModel;

localEntity_t *CG_SmokePuff( const vec3_t p, 
				   const vec3_t vel, 
				   float radius,
				   float r, float g, float b, float a,
				   float duration,
				   int startTime,
				   int fadeInTime,
				   int leFlags,
				   qhandle_t hShader );
void CG_BubbleTrail( vec3_t start, vec3_t end, float spacing );
void CG_SpawnEffect( vec3_t org );
void CG_KamikazeEffect( vec3_t org );
void CG_ObeliskExplode( vec3_t org, int entityNum );
void CG_ObeliskPain( vec3_t org );
void CG_InvulnerabilityImpact( vec3_t org, vec3_t angles );
void CG_InvulnerabilityJuiced( vec3_t org );
void CG_LightningBoltBeam( vec3_t start, vec3_t end );
void CG_LightningDischargeEffect( vec3_t origin, int magnitude );
void CG_ScorePlum( int client, vec3_t org, int score );

void CG_ThawPlayer( vec3_t playerOrigin );
void CG_GibPlayer( vec3_t playerOrigin );
void CG_BigExplode( vec3_t playerOrigin );
void CG_BigExplodeJuiced( vec3_t playerOrigin );

void CG_Bleed( vec3_t origin, int entityNum );

localEntity_t *CG_MakeExplosion( vec3_t origin, vec3_t dir,
								qhandle_t hModel, qhandle_t shader, int msec,
								qboolean isSprite );

//
// cg_snapshot.c
//
void CG_ProcessSnapshots( void );

//
// cg_info.c
//
void CG_ResetLoadingState( void );
void CG_AdvanceLoadingProgress( void );
void CG_LoadingString( const char *s );
void CG_LoadingItem( int itemNum );
void CG_LoadingClient( int clientNum );
void CG_DrawInformation( void );

//
// cg_screen.c
//
void CG_DamageBlendBlob( void );
void CG_DrawJoinGameMenu( void );

//
// cg_scoreboard.c
//
qboolean CG_DrawOldScoreboard( void );
void CG_DrawOldTourneyScoreboard( void );
void CG_BuildHudScoreboard( void );
const cgHudScoreboard_t *CG_GetHudScoreboard( void );
const cgHudScoreboardEntry_t *CG_GetHudScoreboardEntry( int index, team_t team );
int CG_GetHudScoreboardTeamCount( team_t team );
void CG_TouchCompetitiveScores( void );
void CG_StartScoreboardTimer( int startTime );
void CG_StopScoreboardTimer( int stopTime );
int CG_GetScoreboardTimerSeconds( void );

//
// cg_consolecmds.c
//
qboolean CG_ConsoleCommand( void );
void CG_InitConsoleCommands( void );

//
// cg_servercmds.c
//
void CG_ExecuteNewServerCommands( int latestSequence );
void CG_ParseServerinfo( void );
void CG_SetConfigValues( void );
int CG_GetMatchTimeoutStartTime( void );
void CG_ParsePmoveConfigString( const char *payload );
void CG_LoadVoiceChats( void );
void CG_ShaderStateChanged(void);
void CG_VoiceChatLocal( int mode, qboolean voiceOnly, int clientNum, int color, const char *cmd );
void CG_PlayBufferedVoiceChats( void );
void CG_HandleAutoActionsIntermission( const playerState_t *ps );
void CG_RunQueuedAutoActions( void );

qboolean CG_ShouldDrawSpriteSelf( void );
qboolean CG_ShouldDrawTieredArmor( void );
qboolean CG_ShouldDrawSpeedometer( void );
float CG_TeamOverlayXValue( void );
float CG_TeamOverlayYValue( void );
float CG_TeamOverlaySizeValue( void );
float CG_TeamOverlayOpacityValue( void );
qboolean CG_IsSelfOnTeamOverlay( void );

//
// cg_playerstate.c
//
void CG_Respawn( void );
void CG_TransitionPlayerState( playerState_t *ps, playerState_t *ops );
void CG_CheckChangedPredictableEvents( playerState_t *ps );
void pushReward( sfxHandle_t sfx, qhandle_t shader, int rewardCount );


//===============================================

//
// system traps
// These functions are how the cgame communicates with the main game system
//

// print message on the local console
void		trap_Print( const char *fmt );

// abort the game
void		trap_Error( const char *fmt );

// milliseconds should only be used for performance tuning, never
// for anything game related.  Get time from the CG_DrawActiveFrame parameter
int			trap_Milliseconds( void );

// console variable interaction
void		trap_Cvar_Register( vmCvar_t *vmCvar, const char *varName, const char *defaultValue, int flags );
void		trap_Cvar_Update( vmCvar_t *vmCvar );
void		trap_Cvar_Set( const char *var_name, const char *value );
void		trap_Cvar_VariableStringBuffer( const char *var_name, char *buffer, int bufsize );

// ServerCommand and ConsoleCommand parameter access
int			trap_Argc( void );
void		trap_Argv( int n, char *buffer, int bufferLength );
void		trap_Args( char *buffer, int bufferLength );

// filesystem access
// returns length of file
int			trap_FS_FOpenFile( const char *qpath, fileHandle_t *f, fsMode_t mode );
void		trap_FS_Read( void *buffer, int len, fileHandle_t f );
void		trap_FS_Write( const void *buffer, int len, fileHandle_t f );
void		trap_FS_FCloseFile( fileHandle_t f );
int			trap_FS_Seek( fileHandle_t f, long offset, int origin ); // fsOrigin_t

// add commands to the local console as if they were typed in
// for map changing, etc.  The command is not executed immediately,
// but will be executed in order the next time console commands
// are processed
void		trap_SendConsoleCommand( const char *text );

// register a command name so the console can perform command completion.
// FIXME: replace this with a normal console command "defineCommand"?
void		trap_AddCommand( const char *cmdName );

// send a string to the server over the network
void		trap_SendClientCommand( const char *s );

// force a screen update, only used during gamestate load
void		trap_UpdateScreen( void );

// model collision
void		trap_CM_LoadMap( const char *mapname );
int			trap_CM_NumInlineModels( void );
clipHandle_t trap_CM_InlineModel( int index );		// 0 = world, 1+ = bmodels
clipHandle_t trap_CM_TempBoxModel( const vec3_t mins, const vec3_t maxs );
clipHandle_t trap_CM_TempCapsuleModel( const vec3_t mins, const vec3_t maxs );
int			trap_CM_PointContents( const vec3_t p, clipHandle_t model );
int			trap_CM_TransformedPointContents( const vec3_t p, clipHandle_t model, const vec3_t origin, const vec3_t angles );
void		trap_CM_BoxTrace( trace_t *results, const vec3_t start, const vec3_t end,
					  const vec3_t mins, const vec3_t maxs,
					  clipHandle_t model, int brushmask );
void		trap_CM_CapsuleTrace( trace_t *results, const vec3_t start, const vec3_t end,
					  const vec3_t mins, const vec3_t maxs,
					  clipHandle_t model, int brushmask );
void		trap_CM_TransformedBoxTrace( trace_t *results, const vec3_t start, const vec3_t end,
					  const vec3_t mins, const vec3_t maxs,
					  clipHandle_t model, int brushmask,
					  const vec3_t origin, const vec3_t angles );
void		trap_CM_TransformedCapsuleTrace( trace_t *results, const vec3_t start, const vec3_t end,
					  const vec3_t mins, const vec3_t maxs,
					  clipHandle_t model, int brushmask,
					  const vec3_t origin, const vec3_t angles );

// Returns the projection of a polygon onto the solid brushes in the world
int			trap_CM_MarkFragments( int numPoints, const vec3_t *points, 
			const vec3_t projection,
			int maxPoints, vec3_t pointBuffer,
			int maxFragments, markFragment_t *fragmentBuffer );

// normal sounds will have their volume dynamically changed as their entity
// moves and the listener moves
void		trap_S_StartSound( vec3_t origin, int entityNum, int entchannel, sfxHandle_t sfx );
void		trap_S_StopLoopingSound(int entnum);

// a local sound is always played full volume
void		trap_S_StartLocalSound( sfxHandle_t sfx, int channelNum );
void		trap_S_ClearLoopingSounds( qboolean killall );
void		trap_S_AddLoopingSound( int entityNum, const vec3_t origin, const vec3_t velocity, sfxHandle_t sfx );
void		trap_S_AddRealLoopingSound( int entityNum, const vec3_t origin, const vec3_t velocity, sfxHandle_t sfx );
void		trap_S_UpdateEntityPosition( int entityNum, const vec3_t origin );

// respatialize recalculates the volumes of sound as they should be heard by the
// given entityNum and position
void		trap_S_Respatialize( int entityNum, const vec3_t origin, vec3_t axis[3], int inwater );
sfxHandle_t	trap_S_RegisterSound( const char *sample, qboolean compressed );		// returns buzz if not found
void		trap_S_StartBackgroundTrack( const char *intro, const char *loop );	// empty name stops music
void	trap_S_StopBackgroundTrack( void );


void		trap_R_LoadWorldMap( const char *mapname );

// all media should be registered during level startup to prevent
// hitches during gameplay
qhandle_t	trap_R_RegisterModel( const char *name );			// returns rgb axis if not found
qhandle_t	trap_R_RegisterSkin( const char *name );			// returns all white if not found
qhandle_t	trap_R_RegisterShader( const char *name );			// returns all white if not found
qhandle_t	trap_R_RegisterShaderNoMip( const char *name );			// returns all white if not found

// a scene is built up by calls to R_ClearScene and the various R_Add functions.
// Nothing is drawn until R_RenderScene is called.
void		trap_R_ClearScene( void );
void		trap_R_AddRefEntityToScene( const refEntity_t *re );

// polys are intended for simple wall marks, not really for doing
// significant construction
void		trap_R_AddPolyToScene( qhandle_t hShader , int numVerts, const polyVert_t *verts );
void		trap_R_AddPolysToScene( qhandle_t hShader , int numVerts, const polyVert_t *verts, int numPolys );
void		trap_R_AddLightToScene( const vec3_t org, float intensity, float r, float g, float b );
int			trap_R_LightForPoint( vec3_t point, vec3_t ambientLight, vec3_t directedLight, vec3_t lightDir );
void		trap_R_RenderScene( const refdef_t *fd );
void		trap_R_SetColor( const float *rgba );	// NULL = 1,1,1,1
void		trap_R_DrawStretchPic( float x, float y, float w, float h, 
			float s1, float t1, float s2, float t2, qhandle_t hShader );
void		trap_R_ModelBounds( clipHandle_t model, vec3_t mins, vec3_t maxs );
int			trap_R_LerpTag( orientation_t *tag, clipHandle_t mod, int startFrame, int endFrame, 
					   float frac, const char *tagName );
void		trap_R_RemapShader( const char *oldShader, const char *newShader, const char *timeOffset );

// The glconfig_t will not change during the life of a cgame.
// If it needs to change, the entire cgame will be restarted, because
// all the qhandle_t are then invalid.
void		trap_GetGlconfig( glconfig_t *glconfig );

// the gamestate should be grabbed at startup, and whenever a
// configstring changes
void		trap_GetGameState( gameState_t *gamestate );

// cgame will poll each frame to see if a newer snapshot has arrived
// that it is interested in.  The time is returned seperately so that
// snapshot latency can be calculated.
void		trap_GetCurrentSnapshotNumber( int *snapshotNumber, int *serverTime );

// a snapshot get can fail if the snapshot (or the entties it holds) is so
// old that it has fallen out of the client system queue
qboolean	trap_GetSnapshot( int snapshotNumber, snapshot_t *snapshot );

// retrieve a text command from the server stream
// the current snapshot will hold the number of the most recent command
// qfalse can be returned if the client system handled the command
// argc() / argv() can be used to examine the parameters of the command
qboolean	trap_GetServerCommand( int serverCommandNumber );

// returns the most recent command number that can be passed to GetUserCmd
// this will always be at least one higher than the number in the current
// snapshot, and it may be quite a few higher if it is a fast computer on
// a lagged connection
int			trap_GetCurrentCmdNumber( void );	

qboolean	trap_GetUserCmd( int cmdNumber, usercmd_t *ucmd );

// used for the weapon select and zoom
void		trap_SetUserCmdValue( int stateValue, float sensitivityScale );

// aids for VM testing
void		testPrintInt( char *string, int i );
void		testPrintFloat( char *string, float f );

int			trap_MemoryRemaining( void );
void		trap_R_RegisterFont(const char *fontName, int pointSize, fontInfo_t *font);
qboolean	trap_Key_IsDown( int keynum );
int			trap_Key_GetCatcher( void );
void		trap_Key_SetCatcher( int catcher );
int			trap_Key_GetKey( const char *binding );
void		trap_Key_KeynumToStringBuf( int keynum, char *buf, int buflen );
void		trap_Key_GetBindingBuf( int keynum, char *buf, int buflen );
void		trap_Key_SetBinding( int keynum, const char *binding );
qboolean	trap_Key_GetOverstrikeMode( void );
void		trap_Key_SetOverstrikeMode( qboolean state );
void		trap_Cmd_ExecuteText( int exec_when, const char *text );
void		trap_QL_UpdateAdvert( int handleOrToken, int area );
void		trap_AdvertisementBridge_InitCGame( void );
void		trap_AdvertisementBridge_ShutdownCGame( void );
void		trap_AdvertisementBridge_UpdateLoadingViewParameters( void );
void		trap_AdvertisementBridge_SetFrameTime( int frameTime );


typedef enum {
  SYSTEM_PRINT,
  CHAT_PRINT,
  TEAMCHAT_PRINT
} q3print_t; // bk001201 - warning: useless keyword or type name in empty declaration


int trap_CIN_PlayCinematic( const char *arg0, int xpos, int ypos, int width, int height, int bits);
e_status trap_CIN_StopCinematic(int handle);
e_status trap_CIN_RunCinematic (int handle);
void trap_CIN_DrawCinematic (int handle);
void trap_CIN_SetExtents (int handle, int x, int y, int w, int h);

void trap_SnapVector( float *v );

qboolean	trap_loadCamera(const char *name);
void		trap_startCamera(int time);
qboolean	trap_getCameraInfo(int time, vec3_t *origin, vec3_t *angles);

qboolean	trap_GetEntityToken( char *buffer, int bufferSize );
qboolean	trap_R_inPVS( const vec3_t p1, const vec3_t p2 );

void	CG_ClearParticles (void);
void	CG_AddParticles (void);
void	CG_ParticleExplosion (const char *animStr, vec3_t origin, vec3_t vel, int duration, int sizeStart, int sizeEnd);
int CG_NewParticleArea ( int num );

