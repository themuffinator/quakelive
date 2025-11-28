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
// cg_main.c -- initialization and primary entry point for cgame
#include "cg_local.h"

#include "../ui/ui_shared.h"
// display context for new ui stuff
displayContextDef_t cgDC;

#define DEFAULT_WEAPON_BAR_GRENADE_COLOR	"0x007000FF"
#define DEFAULT_SCREEN_DAMAGE_COLOR		"0x700000C8"
#define DEFAULT_SCREEN_DAMAGE_SELF_COLOR	"0x00000000"
#define DEFAULT_SCREEN_DAMAGE_TEAM_COLOR	"0x700000C8"
#define DEFAULT_SCREEN_DAMAGE_ALPHA		"200"

#define CG_AUTOACTION_MAX_RECORDINGS		1000
#define CG_AUTOACTION_SCREENSHOT_DELAY		1000
#define CG_AUTOACTION_STATS_DELAY		1500

int forceModelModificationCount = -1;
int forceTeamModelModificationCount = -1;
int forceTeamSkinModificationCount = -1;
int forceEnemyModelModificationCount = -1;
int forceEnemySkinModificationCount = -1;
int forceTeamWeaponColorModificationCount = -1;
int forceEnemyWeaponColorModificationCount = -1;
int teamHeadColorModificationCount = -1;
int teamUpperColorModificationCount = -1;
int teamLowerColorModificationCount = -1;
int enemyHeadColorModificationCount = -1;
int enemyUpperColorModificationCount = -1;
int enemyLowerColorModificationCount = -1;
static int damagePlumModificationCount = -1;
static int damagePlumColorStyleModificationCount = -1;
int deadBodyDarkenModificationCount = -1;
int deadBodyColorModificationCount = -1;
int screenDamageColorModificationCount = -1;
int screenDamageSelfColorModificationCount = -1;
int screenDamageTeamColorModificationCount = -1;
int screenDamageAlphaModificationCount = -1;
int screenDamageAlphaTeamModificationCount = -1;
int armorTieredModificationCount = -1;
int vignetteModificationCount = -1;
int voiceChatIndicatorModificationCount = -1;
int simpleItemsHeightOffsetModificationCount = -1;
int simpleItemsBobModificationCount = -1;
int simpleItemsRadiusModificationCount = -1;
static int crosshairColorModificationCount = -1;
static int crosshairBrightnessModificationCount = -1;
static int crosshairPulseModificationCount = -1;
static int crosshairHitStyleModificationCount = -1;
static int crosshairHitTimeModificationCount = -1;
static int crosshairHitColorModificationCount = -1;

void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum );
void CG_Shutdown( void );
static void CG_UpdateSimpleItemsSettings( void );
static void CG_UpdateCrosshairColorSettings( void );
static void CG_UpdateCrosshairPulseSettings( void );
static void CG_UpdateCrosshairHitSettings( void );
static void CG_UpdateAutomationSettings( void );
static void CG_ClearAutomationState( void );


/*
================
vmMain

This is the only way control passes into the module.
This must be the very first function compiled into the .q3vm file
================
*/
int vmMain( int command, int arg0, int arg1, int arg2, int arg3, int arg4, int arg5, int arg6, int arg7, int arg8, int arg9, int arg10, int arg11  ) {

	switch ( command ) {
	case CG_INIT:
		CG_Init( arg0, arg1, arg2 );
		return 0;
	case CG_SHUTDOWN:
		CG_Shutdown();
		return 0;
	case CG_CONSOLE_COMMAND:
		return CG_ConsoleCommand();
	case CG_DRAW_ACTIVE_FRAME:
		CG_DrawActiveFrame( arg0, arg1, arg2 );
		return 0;
	case CG_CROSSHAIR_PLAYER:
		return CG_CrosshairPlayer();
	case CG_LAST_ATTACKER:
		return CG_LastAttacker();
	case CG_KEY_EVENT:
		CG_KeyEvent(arg0, arg1);
		return 0;
	case CG_MOUSE_EVENT:
		cgDC.cursorx = cgs.cursorX;
		cgDC.cursory = cgs.cursorY;
		CG_MouseEvent(arg0, arg1);
		return 0;
	case CG_EVENT_HANDLING:
		CG_EventHandling(arg0);
		return 0;
	default:
		CG_Error( "vmMain: unknown command %i", command );
		break;
	}
	return -1;
}


cg_t				cg;
cgs_t				cgs;
centity_t			cg_entities[MAX_GENTITIES];
weaponInfo_t		cg_weapons[MAX_WEAPONS];
itemInfo_t			cg_items[MAX_ITEMS];
pmove_settings_t		cg_pmoveSettings;


static int		weaponColorGrenadeModCount = -1;
static int		lowAmmoWarningPercentileModCount = -1;
static int		announcerModificationCount = -1;

vmCvar_t	cg_railTrailTime;
vmCvar_t	cg_centertime;
vmCvar_t	cg_runpitch;
vmCvar_t	cg_runroll;
vmCvar_t	cg_bobup;
vmCvar_t	cg_bobpitch;
vmCvar_t	cg_bobroll;
vmCvar_t	cg_bob;
vmCvar_t	cg_swingSpeed;
vmCvar_t	cg_shadows;
vmCvar_t	cg_gibs;
vmCvar_t	cg_drawTimer;
vmCvar_t	cg_drawFPS;
vmCvar_t	cg_drawSnapshot;
vmCvar_t	cg_draw3dIcons;
vmCvar_t	cg_drawIcons;
vmCvar_t	cg_drawAmmoWarning;
vmCvar_t	cg_drawCrosshair;
vmCvar_t	cg_drawCrosshairNames;
vmCvar_t	cg_drawRewards;
vmCvar_t	cg_drawRewardsRowSize;
vmCvar_t	cg_announcer;
vmCvar_t	cg_announcerRewardsVO;
vmCvar_t	cg_raceBeep;
vmCvar_t	cg_drawCheckpointRemaining;
vmCvar_t	cg_levelTimerDirection;
vmCvar_t	cg_raceBeep;
vmCvar_t	cg_drawProfileImages;
vmCvar_t	cg_drawSprites;
vmCvar_t	cg_drawPregameMessages;
vmCvar_t	cg_drawSpecMessages;
vmCvar_t	cg_drawItemPickups;
vmCvar_t	cg_drawSpriteSelf;
vmCvar_t	cg_drawDemoHUD;
vmCvar_t	cg_drawFragMessages;
vmCvar_t	cg_drawInputCmds;
vmCvar_t	cg_drawInputCmdsX;
vmCvar_t	cg_drawInputCmdsY;
vmCvar_t	cg_drawInputCmdsSize;
vmCvar_t	cg_weaponBar;
vmCvar_t	cg_weaponColor_grenade;
vmCvar_t	cg_weaponConfig;
vmCvar_t	cg_weaponConfig_g;
vmCvar_t	cg_weaponConfig_mg;
vmCvar_t	cg_weaponConfig_sg;
vmCvar_t	cg_weaponConfig_gl;
vmCvar_t	cg_weaponConfig_rl;
vmCvar_t	cg_weaponConfig_lg;
vmCvar_t	cg_weaponConfig_rg;
vmCvar_t	cg_weaponConfig_pg;
vmCvar_t	cg_weaponConfig_bfg;
vmCvar_t	cg_weaponConfig_gh;
vmCvar_t	cg_weaponConfig_ng;
vmCvar_t	cg_weaponConfig_pl;
vmCvar_t	cg_weaponConfig_cg;
vmCvar_t	cg_weaponConfig_hmg;
vmCvar_t	cg_weaponPrimary;
vmCvar_t	cg_weaponPrimaryQueued;
vmCvar_t	cg_crosshairSize;
vmCvar_t	cg_crosshairX;
vmCvar_t	cg_crosshairY;
vmCvar_t	cg_crosshairHealth;
vmCvar_t	cg_crosshairColor;
vmCvar_t	cg_crosshairBrightness;
vmCvar_t	cg_crosshairPulse;
vmCvar_t	cg_crosshairHitStyle;
vmCvar_t	cg_crosshairHitTime;
vmCvar_t	cg_crosshairHitColor;
vmCvar_t	cg_enemyCrosshairNames;
vmCvar_t	cg_enemyCrosshairNamesOpacity;
vmCvar_t	cg_teammateCrosshairNames;
vmCvar_t	cg_teammateCrosshairNamesOpacity;
vmCvar_t	cg_drawCrosshairTeamHealth;
vmCvar_t	cg_drawCrosshairTeamHealthSize;
vmCvar_t	cg_draw2D;
vmCvar_t	cg_drawStatus;
vmCvar_t	cg_animSpeed;
vmCvar_t	cg_debugAnim;
vmCvar_t	cg_debugPosition;
vmCvar_t	cg_debugEvents;
vmCvar_t	cg_errorDecay;
vmCvar_t	cg_nopredict;
vmCvar_t	cg_noPlayerAnims;
vmCvar_t	cg_showmiss;
vmCvar_t	cg_footsteps;
vmCvar_t	cg_addMarks;
vmCvar_t	cg_brassTime;
vmCvar_t	cg_viewsize;
vmCvar_t	cg_drawGun;
vmCvar_t	cg_gun_frame;
vmCvar_t	cg_gun_x;
vmCvar_t	cg_gun_y;
vmCvar_t	cg_gun_z;
vmCvar_t	cg_tracerChance;
vmCvar_t	cg_tracerWidth;
vmCvar_t	cg_tracerLength;
vmCvar_t	cg_autoHop;
vmCvar_t	cg_autoProjectileNudge;
vmCvar_t	cg_autoswitch;
vmCvar_t	cg_projectileNudge;
vmCvar_t	cg_switchOnEmpty;
vmCvar_t	cg_switchToEmpty;
vmCvar_t	cg_ignore;
vmCvar_t	cg_simpleItems;
vmCvar_t	cg_simpleItemsHeightOffset;
vmCvar_t	cg_simpleItemsBob;
vmCvar_t	cg_simpleItemsRadius;
vmCvar_t	cg_fov;
vmCvar_t	cg_zoomFov;
vmCvar_t	cg_zoomToggle;
vmCvar_t	cg_zoomOutOnDeath;
vmCvar_t	cg_zoomScaling;
vmCvar_t	cg_zoomSensitivity;
vmCvar_t	cg_waterWarp;
vmCvar_t	cg_thirdPerson;
vmCvar_t	cg_thirdPersonRange;
vmCvar_t	cg_thirdPersonAngle;
vmCvar_t	cg_thirdPersonPitch;
vmCvar_t	cg_stereoSeparation;
vmCvar_t	cg_lagometer;
vmCvar_t	cg_drawAttacker;
vmCvar_t	cg_synchronousClients;
vmCvar_t 	cg_teamChatTime;
vmCvar_t 	cg_lowAmmoWarningPercentile;
vmCvar_t 	cg_teamChatHeight;
vmCvar_t	cg_chatHistoryLength;
vmCvar_t	cg_chatbeep;
vmCvar_t	cg_teamChatBeep;
vmCvar_t 	cg_stats;
vmCvar_t 	cg_buildScript;
vmCvar_t 	cg_forceModel;
vmCvar_t	cg_forceTeamModel;
vmCvar_t	cg_forceTeamSkin;
vmCvar_t	cg_forceEnemyModel;
vmCvar_t	cg_forceEnemySkin;
vmCvar_t	cg_forceTeamWeaponColor;
vmCvar_t	cg_forceEnemyWeaponColor;
vmCvar_t	cg_teamHeadColor;
vmCvar_t	cg_teamUpperColor;
vmCvar_t	cg_teamLowerColor;
vmCvar_t	cg_enemyHeadColor;
vmCvar_t	cg_enemyUpperColor;
vmCvar_t	cg_enemyLowerColor;
vmCvar_t	cg_paused;
vmCvar_t	cg_blood;
vmCvar_t	cg_predictItems;
vmCvar_t	cg_deferPlayers;
vmCvar_t	cg_drawTeamOverlay;
vmCvar_t	cg_selfOnTeamOverlay;
vmCvar_t	cg_drawTeamOverlayX;
vmCvar_t	cg_drawTeamOverlayY;
vmCvar_t	cg_drawTeamOverlaySize;
vmCvar_t	cg_drawTeamOverlayOpacity;
vmCvar_t	cg_teamOverlayUserinfo;
vmCvar_t	cg_drawFriend;
vmCvar_t	cg_teammateNames;
vmCvar_t	cg_teammatePOIs;
vmCvar_t	cg_teammatePOIsMinWidth;
vmCvar_t	cg_teammatePOIsMaxWidth;
vmCvar_t	cg_teamChatsOnly;
vmCvar_t	cg_playVoiceChats;
vmCvar_t	cg_showVoiceText;
vmCvar_t	cg_useItemMessage;
vmCvar_t	cg_useItemWarning;
vmCvar_t	cg_allowTaunt;
vmCvar_t	cg_muzzleFlash;
vmCvar_t	cg_hudFiles;
vmCvar_t	cg_kickScale;
vmCvar_t 	cg_scorePlum;
vmCvar_t 	cg_damagePlum;
vmCvar_t 	cg_damagePlumColorStyle;
vmCvar_t 	cg_preferredStartingWeapons;
vmCvar_t 	cg_disableLoadout_g;
vmCvar_t 	cg_disableLoadout_mg;
vmCvar_t 	cg_disableLoadout_sg;
vmCvar_t 	cg_disableLoadout_gl;
vmCvar_t 	cg_disableLoadout_rl;
vmCvar_t 	cg_disableLoadout_lg;
vmCvar_t 	cg_disableLoadout_rg;
vmCvar_t 	cg_disableLoadout_pg;
vmCvar_t 	cg_disableLoadout_bfg;
vmCvar_t 	cg_disableLoadout_gh;
vmCvar_t 	cg_disableLoadout_ng;
vmCvar_t 	cg_disableLoadout_pl;
vmCvar_t 	cg_disableLoadout_cg;
vmCvar_t 	cg_disableLoadout_hmg;
vmCvar_t 	cg_trueShotgun;
vmCvar_t 	cg_trackPlayer;
vmCvar_t 	cg_followKiller;
vmCvar_t 	cg_followPowerup;
vmCvar_t 	cg_ignoreMouseInput;
vmCvar_t 	cg_filter_angles;
vmCvar_t 	cg_smoothClients;
vmCvar_t 	cg_loadout;
vmCvar_t	pmove_fixed;
//vmCvar_t	cg_pmove_fixed;
vmCvar_t	pmove_msec;
vmCvar_t	cg_pmove_msec;
vmCvar_t	cg_cameraMode;
vmCvar_t	cg_cameraOrbit;
vmCvar_t	cg_cameraOrbitDelay;
vmCvar_t	cg_timescaleFadeEnd;
vmCvar_t	cg_timescaleFadeSpeed;
vmCvar_t	cg_timescale;
vmCvar_t	cg_smallFont;
vmCvar_t	cg_bigFont;
vmCvar_t	cg_noTaunt;
vmCvar_t	cg_noProjectileTrail;
vmCvar_t	cg_oldRail;
vmCvar_t	cg_oldRocket;
vmCvar_t	cg_oldPlasma;
vmCvar_t	cg_trueLightning;
vmCvar_t	cg_predictLocalRailshots;
vmCvar_t	cg_lightningStyle;
vmCvar_t	cg_lightningImpact;
vmCvar_t	cg_lightningImpactCap;
vmCvar_t	cg_drawTieredArmorAvailability;
vmCvar_t	cg_armorTiered;
vmCvar_t	cg_drawFullWeaponBar;
vmCvar_t	cg_drawHitFriendTime;
vmCvar_t	cg_drawDeadFriendTime;
vmCvar_t	cg_deadBodyDarken;
vmCvar_t	cg_deadBodyColor;
vmCvar_t	cg_speedometer;
vmCvar_t	cg_specNames;
vmCvar_t	cg_specItemTimers;
vmCvar_t	cg_specItemTimersX;
vmCvar_t	cg_specItemTimersY;
vmCvar_t	cg_specItemTimersSize;
vmCvar_t	cg_specTeamVitals;
vmCvar_t	cg_specTeamVitalsHealthColor;
vmCvar_t	cg_itemTimers;
vmCvar_t	cg_screenDamage;
vmCvar_t	cg_screenDamage_Self;
vmCvar_t	cg_screenDamage_Team;
vmCvar_t	cg_screenDamageAlpha;
vmCvar_t	cg_screenDamageAlpha_Team;
vmCvar_t	cg_overheadNamesWidth;
vmCvar_t	cg_obituaryRowSize;
vmCvar_t	cg_spectating;
vmCvar_t	cg_gametype;
vmCvar_t	cg_gameInfo1;
vmCvar_t	cg_gameInfo2;
vmCvar_t	cg_gameInfo3;
vmCvar_t	cg_gameInfo4;
vmCvar_t	cg_gameInfo5;
vmCvar_t	cg_gameInfo6;
vmCvar_t	cg_useLegacyHud;
vmCvar_t	cg_vignette;
vmCvar_t	cg_voiceChatIndicator;
vmCvar_t	cg_autoHop;
vmCvar_t	cg_autoProjectileNudge;
vmCvar_t	cg_projectileNudge;
vmCvar_t	cg_predictLocalRailshots;
vmCvar_t	cg_autoAction;

vmCvar_t 	cg_redTeamName;
vmCvar_t 	cg_blueTeamName;
vmCvar_t	cg_currentSelectedPlayer;
vmCvar_t	cg_currentSelectedPlayerName;
vmCvar_t	cg_singlePlayer;
vmCvar_t	cg_enableDust;
vmCvar_t	cg_enableBreath;
vmCvar_t	cg_singlePlayerActive;
vmCvar_t	cg_recordSPDemo;
vmCvar_t	cg_recordSPDemoName;
vmCvar_t	cg_obeliskRespawnDelay;
vmCvar_t	cg_lastmsg;

typedef struct {
	vmCvar_t	*vmCvar;
	char		*cvarName;
	char		*defaultString;
	int			cvarFlags;
} cvarTable_t;

static unsigned int CG_ParseDamagePlumWeaponValue( const char *value, damagePlumPreset_t *preset );
static damagePlumColorStyle_t CG_ParseDamagePlumColorStyleValue( int rawValue );
static void CG_UpdateDamagePlumSettings( void );
static sfxHandle_t CG_RegisterAnnouncerClip( const char *folder, const char *sample );
static void CG_RegisterAnnouncerVoiceSet( cgAnnouncerProfile_t profile, const char *folder );
static sfxHandle_t CG_RegisterRaceCueSound( const char *name );
static void CG_SetActiveAnnouncerProfile( cgAnnouncerProfile_t profile );
static void CG_UpdateAnnouncerProfileFromCvar( qboolean force );
static qboolean CG_ParseLastMessageValue( const char *value, int *timestamp, char *message, int messageSize );
static void CG_WriteLastMessageCvar( int timestamp, const char *message );
static void CG_ReplayLastMessageFromCvar( void );

static cvarTable_t cvarTable[] = { // bk001129
	{ &cg_ignore, "cg_ignore", "0", 0 },	// used for debugging
	{ &cg_autoHop, "cg_autoHop", "1", CVAR_ARCHIVE },
	{ &cg_autoProjectileNudge, "cg_autoProjectileNudge", "0", CVAR_ARCHIVE },
	{ &cg_projectileNudge, "cg_projectileNudge", "0", CVAR_ARCHIVE },
	{ &cg_autoswitch, "cg_autoswitch", "1", CVAR_ARCHIVE },
	{ &cg_switchOnEmpty, "cg_switchOnEmpty", "1", CVAR_ARCHIVE },
	{ &cg_switchToEmpty, "cg_switchToEmpty", "1", CVAR_ARCHIVE },
	{ &cg_drawGun, "cg_drawGun", "1", CVAR_ARCHIVE },
	{ &cg_zoomFov, "cg_zoomfov", "22.5", CVAR_ARCHIVE },
	{ &cg_zoomToggle, "cg_zoomToggle", "0", CVAR_ARCHIVE },
	{ &cg_zoomOutOnDeath, "cg_zoomOutOnDeath", "0", CVAR_ARCHIVE },
	{ &cg_zoomScaling, "cg_zoomScaling", "1", CVAR_ARCHIVE },
	{ &cg_zoomSensitivity, "cg_zoomSensitivity", "1", CVAR_ARCHIVE },
	{ &cg_waterWarp, "cg_waterWarp", "1", CVAR_ARCHIVE },
	{ &cg_fov, "cg_fov", "90", CVAR_ARCHIVE },
	{ &cg_viewsize, "cg_viewsize", "100", CVAR_ARCHIVE },
	{ &cg_stereoSeparation, "cg_stereoSeparation", "0.4", CVAR_ARCHIVE  },
	{ &cg_shadows, "cg_shadows", "1", CVAR_ARCHIVE  },
	{ &cg_gibs, "cg_gibs", "1", CVAR_ARCHIVE  },
	{ &cg_draw2D, "cg_draw2D", "1", CVAR_ARCHIVE  },
	{ &cg_drawStatus, "cg_drawStatus", "1", CVAR_ARCHIVE  },
	{ &cg_useLegacyHud, "cg_useLegacyHud", "0", CVAR_ARCHIVE },
	{ &cg_vignette, "cg_vignette", "1", CVAR_ARCHIVE },
	{ &cg_drawTimer, "cg_drawTimer", "0", CVAR_ARCHIVE  },
	{ &cg_levelTimerDirection, "cg_levelTimerDirection", "up", CVAR_ARCHIVE },
	{ &cg_drawFPS, "cg_drawFPS", "0", CVAR_ARCHIVE  },
	{ &cg_drawSnapshot, "cg_drawSnapshot", "0", CVAR_ARCHIVE  },
	{ &cg_draw3dIcons, "cg_draw3dIcons", "1", CVAR_ARCHIVE  },
	{ &cg_drawIcons, "cg_drawIcons", "1", CVAR_ARCHIVE  },
	{ &cg_drawAmmoWarning, "cg_drawAmmoWarning", "1", CVAR_ARCHIVE  },
	{ &cg_lowAmmoWarningPercentile, "cg_lowAmmoWarningPercentile", "0.20", CVAR_ARCHIVE },
	{ &cg_drawAttacker, "cg_drawAttacker", "1", CVAR_ARCHIVE  },
	{ &cg_drawCrosshair, "cg_drawCrosshair", "4", CVAR_ARCHIVE },
	{ &cg_drawCrosshairNames, "cg_drawCrosshairNames", "1", CVAR_ARCHIVE },
	{ &cg_drawRewards, "cg_drawRewards", "1", CVAR_ARCHIVE },
	{ &cg_drawRewardsRowSize, "cg_drawRewardsRowSize", "9", CVAR_ARCHIVE },
	{ &cg_announcer, "cg_announcer", "1", CVAR_ARCHIVE },
	{ &cg_announcerRewardsVO, "cg_announcerRewardsVO", "1", CVAR_ARCHIVE },
	{ &cg_raceBeep, "cg_raceBeep", "1", CVAR_ARCHIVE },
	{ &cg_drawCheckpointRemaining, "cg_drawCheckpointRemaining", "1", CVAR_ARCHIVE },
	{ &cg_raceBeep, "cg_raceBeep", "1", CVAR_ARCHIVE },
	{ &cg_drawProfileImages, "cg_drawProfileImages", "1", CVAR_ARCHIVE },
	{ &cg_drawSprites, "cg_drawSprites", "1", CVAR_ARCHIVE },
	{ &cg_drawPregameMessages, "cg_drawPregameMessages", "1", CVAR_ARCHIVE },
	{ &cg_drawSpecMessages, "cg_drawSpecMessages", "1", CVAR_ARCHIVE },
	{ &cg_useItemMessage, "cg_useItemMessage", "1", CVAR_ARCHIVE },
	{ &cg_useItemWarning, "cg_useItemWarning", "1", CVAR_ARCHIVE },
	{ &cg_allowTaunt, "cg_allowTaunt", "1", CVAR_ARCHIVE },
	{ &cg_muzzleFlash, "cg_muzzleFlash", "1", CVAR_ARCHIVE },
{ &cg_drawItemPickups, "cg_drawItemPickups", "5", CVAR_ARCHIVE },
{ &cg_drawSpriteSelf, "cg_drawSpriteSelf", "0", CVAR_ARCHIVE },
{ &cg_drawDemoHUD, "cg_drawDemoHUD", "1", CVAR_ARCHIVE },
{ &cg_drawFragMessages, "cg_drawFragMessages", "1", CVAR_ARCHIVE },
{ &cg_drawInputCmds, "cg_drawInputCmds", "0", CVAR_ARCHIVE },
	{ &cg_drawInputCmdsX, "cg_drawInputCmdsX", "640", CVAR_ARCHIVE },
	{ &cg_drawInputCmdsY, "cg_drawInputCmdsY", "480", CVAR_ARCHIVE },
	{ &cg_drawInputCmdsSize, "cg_drawInputCmdsSize", "16", CVAR_ARCHIVE },
{ &cg_crosshairSize, "cg_crosshairSize", "24", CVAR_ARCHIVE },
{ &cg_crosshairHealth, "cg_crosshairHealth", "1", CVAR_ARCHIVE },
{ &cg_crosshairColor, "cg_crosshairColor", "4", CVAR_ARCHIVE },
{ &cg_crosshairBrightness, "cg_crosshairBrightness", "1", CVAR_ARCHIVE },
{ &cg_crosshairPulse, "cg_crosshairPulse", "1", CVAR_ARCHIVE },
{ &cg_crosshairHitStyle, "cg_crosshairHitStyle", "2", CVAR_ARCHIVE },
{ &cg_crosshairHitTime, "cg_crosshairHitTime", "200", CVAR_ARCHIVE },
{ &cg_crosshairHitColor, "cg_crosshairHitColor", "1", CVAR_ARCHIVE },
{ &cg_enemyCrosshairNames, "cg_enemyCrosshairNames", "1", CVAR_ARCHIVE },
{ &cg_enemyCrosshairNamesOpacity, "cg_enemyCrosshairNamesOpacity", "0.75", CVAR_ARCHIVE },
{ &cg_teammateCrosshairNames, "cg_teammateCrosshairNames", "1", CVAR_ARCHIVE },
{ &cg_teammateCrosshairNamesOpacity, "cg_teammateCrosshairNamesOpacity", "0.75", CVAR_ARCHIVE },
{ &cg_drawCrosshairTeamHealth, "cg_drawCrosshairTeamHealth", "29", CVAR_ARCHIVE },
	{ &cg_drawCrosshairTeamHealthSize, "cg_drawCrosshairTeamHealthSize", "0.12", CVAR_ARCHIVE },
	{ &cg_crosshairX, "cg_crosshairX", "0", CVAR_ARCHIVE },
	{ &cg_crosshairY, "cg_crosshairY", "0", CVAR_ARCHIVE },
	{ &cg_brassTime, "cg_brassTime", "2500", CVAR_ARCHIVE },
	{ &cg_simpleItems, "cg_simpleItems", "0", CVAR_ARCHIVE },
	{ &cg_simpleItemsHeightOffset, "cg_simpleItemsHeightOffset", "0", CVAR_ARCHIVE },
	{ &cg_simpleItemsBob, "cg_simpleItemsBob", "0", CVAR_ARCHIVE },
	{ &cg_simpleItemsRadius, "cg_simpleItemsRadius", "14", CVAR_ARCHIVE },
	{ &cg_addMarks, "cg_marks", "1", CVAR_ARCHIVE },
	{ &cg_lagometer, "cg_lagometer", "1", CVAR_ARCHIVE },
	{ &cg_railTrailTime, "cg_railTrailTime", "400", CVAR_ARCHIVE  },
	{ &cg_gun_x, "cg_gunX", "0", CVAR_CHEAT },
	{ &cg_gun_y, "cg_gunY", "0", CVAR_CHEAT },
	{ &cg_gun_z, "cg_gunZ", "0", CVAR_CHEAT },
	{ &cg_centertime, "cg_centertime", "3", CVAR_CHEAT },
	{ &cg_runpitch, "cg_runpitch", "0.002", CVAR_ARCHIVE},
	{ &cg_runroll, "cg_runroll", "0.005", CVAR_ARCHIVE },
	{ &cg_bobup , "cg_bobup", "0.005", CVAR_CHEAT },
	{ &cg_bobpitch, "cg_bobpitch", "0.002", CVAR_ARCHIVE },
	{ &cg_bobroll, "cg_bobroll", "0.002", CVAR_ARCHIVE },
	{ &cg_bob, "cg_bob", "1", CVAR_ARCHIVE },
	{ &cg_kickScale, "cg_kickScale", "1", CVAR_ARCHIVE },
	{ &cg_swingSpeed, "cg_swingSpeed", "0.3", CVAR_CHEAT },
	{ &cg_animSpeed, "cg_animspeed", "1", CVAR_CHEAT },
	{ &cg_debugAnim, "cg_debuganim", "0", CVAR_CHEAT },
	{ &cg_debugPosition, "cg_debugposition", "0", CVAR_CHEAT },
	{ &cg_debugEvents, "cg_debugevents", "0", CVAR_CHEAT },
	{ &cg_errorDecay, "cg_errordecay", "100", 0 },
	{ &cg_nopredict, "cg_nopredict", "0", 0 },
	{ &cg_noPlayerAnims, "cg_noplayeranims", "0", CVAR_CHEAT },
	{ &cg_showmiss, "cg_showmiss", "0", 0 },
	{ &cg_footsteps, "cg_footsteps", "1", CVAR_CHEAT },
	{ &cg_tracerChance, "cg_tracerchance", "0.4", CVAR_CHEAT },
	{ &cg_tracerWidth, "cg_tracerwidth", "1", CVAR_CHEAT },
	{ &cg_tracerLength, "cg_tracerlength", "100", CVAR_CHEAT },
	{ &cg_thirdPersonRange, "cg_thirdPersonRange", "40", CVAR_CHEAT },
	{ &cg_thirdPersonAngle, "cg_thirdPersonAngle", "0", CVAR_CHEAT },
	{ &cg_thirdPersonPitch, "cg_thirdPersonPitch", "4.0", CVAR_CHEAT },
	{ &cg_thirdPerson, "cg_thirdPerson", "0", 0 },
{ &cg_teamChatTime, "cg_teamChatTime", "3000", CVAR_ARCHIVE  },
{ &cg_teamChatHeight, "cg_teamChatHeight", "0", CVAR_ARCHIVE  },
{ &cg_chatHistoryLength, "cg_chatHistoryLength", "0", CVAR_ARCHIVE },
{ &cg_chatbeep, "cg_chatbeep", "1", CVAR_ARCHIVE },
{ &cg_teamChatBeep, "cg_teamChatBeep", "1", CVAR_ARCHIVE },
	{ &cg_forceModel, "cg_forceModel", "0", CVAR_ARCHIVE  },
	{ &cg_forceTeamModel, "cg_forceTeamModel", "", CVAR_ARCHIVE },
	{ &cg_forceTeamSkin, "cg_forceTeamSkin", "", CVAR_ARCHIVE },
	{ &cg_forceEnemyModel, "cg_forceEnemyModel", "", CVAR_ARCHIVE },
	{ &cg_forceEnemySkin, "cg_forceEnemySkin", "", CVAR_ARCHIVE },
	{ &cg_forceTeamWeaponColor, "cg_forceTeamWeaponColor", "0", CVAR_ARCHIVE },
	{ &cg_forceEnemyWeaponColor, "cg_forceEnemyWeaponColor", "0", CVAR_ARCHIVE },
	{ &cg_teamHeadColor, "cg_teamHeadColor", "", CVAR_ARCHIVE },
	{ &cg_teamUpperColor, "cg_teamUpperColor", "", CVAR_ARCHIVE },
	{ &cg_teamLowerColor, "cg_teamLowerColor", "", CVAR_ARCHIVE },
	{ &cg_enemyHeadColor, "cg_enemyHeadColor", "", CVAR_ARCHIVE },
	{ &cg_enemyUpperColor, "cg_enemyUpperColor", "", CVAR_ARCHIVE },
	{ &cg_enemyLowerColor, "cg_enemyLowerColor", "", CVAR_ARCHIVE },
	{ &cg_predictItems, "cg_predictItems", "1", CVAR_ARCHIVE },
	{ &cg_deferPlayers, "cg_deferPlayers", "0", CVAR_ARCHIVE },
	{ &cg_drawTeamOverlay, "cg_drawTeamOverlay", "0", CVAR_ARCHIVE },
	{ &cg_selfOnTeamOverlay, "cg_selfOnTeamOverlay", "0", CVAR_ARCHIVE },
	{ &cg_drawTeamOverlayX, "cg_drawTeamOverlayX", "-640", CVAR_ARCHIVE },
	{ &cg_drawTeamOverlayY, "cg_drawTeamOverlayY", "-480", CVAR_ARCHIVE },
	{ &cg_drawTeamOverlaySize, "cg_drawTeamOverlaySize", "0.16", CVAR_ARCHIVE },
	{ &cg_drawTeamOverlayOpacity, "cg_drawTeamOverlayOpacity", "0.75", CVAR_ARCHIVE },
	{ &cg_teamOverlayUserinfo, "teamoverlay", "0", CVAR_ROM | CVAR_USERINFO },
	{ &cg_stats, "cg_stats", "0", 0 },
	{ &cg_drawFriend, "cg_drawFriend", "1", CVAR_ARCHIVE },
	{ &cg_teammateNames, "cg_teammateNames", "1", CVAR_ARCHIVE },
	{ &cg_teammatePOIs, "cg_teammatePOIs", "1", CVAR_ARCHIVE },
	{ &cg_teammatePOIsMinWidth, "cg_teammatePOIsMinWidth", "4.0", CVAR_ARCHIVE },
	{ &cg_teammatePOIsMaxWidth, "cg_teammatePOIsMaxWidth", "24.0", CVAR_ARCHIVE },
	{ &cg_teamChatsOnly, "cg_teamChatsOnly", "0", CVAR_ARCHIVE },
	{ &cg_noVoiceChats, "cg_noVoiceChats", "0", CVAR_ARCHIVE },
	{ &cg_noVoiceText, "cg_noVoiceText", "0", CVAR_ARCHIVE },
	{ &cg_voiceChatIndicator, "cg_voiceChatIndicator", "1", CVAR_ARCHIVE },
	{ &cg_autoHop, "cg_autoHop", "0", CVAR_ARCHIVE | CVAR_LATCH },
	{ &cg_autoProjectileNudge, "cg_autoProjectileNudge", "0", CVAR_ARCHIVE | CVAR_LATCH },
	{ &cg_projectileNudge, "cg_projectileNudge", "0", CVAR_ARCHIVE | CVAR_LATCH },
	{ &cg_predictLocalRailshots, "cg_predictLocalRailshots", "0", CVAR_ARCHIVE | CVAR_LATCH },
	{ &cg_autoAction, "cg_autoAction", "0", CVAR_ARCHIVE | CVAR_LATCH },
{ &cg_teamChatsOnly, "cg_teamChatsOnly", "0", CVAR_ARCHIVE },
{ &cg_playVoiceChats, "cg_playVoiceChats", "1", CVAR_ARCHIVE },
{ &cg_showVoiceText, "cg_showVoiceText", "1", CVAR_ARCHIVE },
{ &cg_voiceChatIndicator, "cg_voiceChatIndicator", "1", CVAR_ARCHIVE },
	// the following variables are created in other parts of the system,
	// but we also reference them here
	{ &cg_buildScript, "com_buildScript", "0", 0 },	// force loading of all possible data amd error on failures
	{ &cg_paused, "cl_paused", "0", CVAR_ROM },
	{ &cg_blood, "com_blood", "1", CVAR_ARCHIVE },
	{ &cg_synchronousClients, "g_synchronousClients", "0", 0 },	// communicated by systeminfo
	{ &cg_redTeamName, "g_redteam", DEFAULT_REDTEAM_NAME, CVAR_ARCHIVE },
	{ &cg_blueTeamName, "g_blueteam", DEFAULT_BLUETEAM_NAME, CVAR_ARCHIVE },
	{ &cg_currentSelectedPlayer, "cg_currentSelectedPlayer", "0", CVAR_ARCHIVE},
	{ &cg_currentSelectedPlayerName, "cg_currentSelectedPlayerName", "", CVAR_ARCHIVE},
	{ &cg_singlePlayer, "ui_singlePlayerActive", "0", CVAR_USERINFO},
	{ &cg_enableDust, "g_enableDust", "0", CVAR_SERVERINFO},
	{ &cg_enableBreath, "g_enableBreath", "0", CVAR_SERVERINFO},
	{ &cg_singlePlayerActive, "ui_singlePlayerActive", "0", CVAR_USERINFO},
	{ &cg_recordSPDemo, "ui_recordSPDemo", "0", CVAR_ARCHIVE},
	{ &cg_recordSPDemoName, "ui_recordSPDemoName", "", CVAR_ARCHIVE},
	{ &cg_obeliskRespawnDelay, "g_obeliskRespawnDelay", "10", CVAR_SERVERINFO},
	{ &cg_lastmsg, "cg_lastmsg", "0", CVAR_ARCHIVE },
	{ &cg_hudFiles, "cg_hudFiles", CG_DEFAULT_HUD_FILE, CVAR_ARCHIVE},
	{ &cg_cameraOrbit, "cg_cameraOrbit", "0", CVAR_CHEAT},
	{ &cg_cameraOrbitDelay, "cg_cameraOrbitDelay", "50", CVAR_ARCHIVE},
	{ &cg_timescaleFadeEnd, "cg_timescaleFadeEnd", "1", 0},
	{ &cg_timescaleFadeSpeed, "cg_timescaleFadeSpeed", "0", 0},
	{ &cg_timescale, "timescale", "1", 0},
	{ &cg_scorePlum, "cg_scorePlums", "1", CVAR_USERINFO | CVAR_ARCHIVE},
	{ &cg_damagePlum, "cg_damagePlum", "g mg sg gl rl lg rg pg bfg gh cg ng pl hmg", CVAR_USERINFO | CVAR_ARCHIVE },
	{ &cg_damagePlumColorStyle, "cg_damagePlumColorStyle", "1", CVAR_ARCHIVE },
	{ &cg_smoothClients, "cg_smoothClients", "0", CVAR_USERINFO | CVAR_ARCHIVE},
	{ &cg_cameraMode, "com_cameraMode", "0", CVAR_CHEAT},

	{ &pmove_fixed, "pmove_fixed", "0", 0},
	{ &pmove_msec, "pmove_msec", "8", 0},
	{ &cg_noTaunt, "cg_noTaunt", "0", CVAR_ARCHIVE},
	{ &cg_noProjectileTrail, "cg_noProjectileTrail", "0", CVAR_ARCHIVE},
	{ &cg_smallFont, "ui_smallFont", "0.25", CVAR_ARCHIVE},
	{ &cg_bigFont, "ui_bigFont", "0.4", CVAR_ARCHIVE},
	{ &cg_oldRail, "cg_oldRail", "1", CVAR_ARCHIVE},
	{ &cg_oldRocket, "cg_oldRocket", "1", CVAR_ARCHIVE},
	{ &cg_oldPlasma, "cg_oldPlasma", "1", CVAR_ARCHIVE},
	{ &cg_trueLightning, "cg_trueLightning", "0.0", CVAR_ARCHIVE },
	{ &cg_predictLocalRailshots, "cg_predictLocalRailshots", "0", CVAR_ARCHIVE },
	{ &cg_lightningStyle, "cg_lightningStyle", "1", CVAR_ARCHIVE },
	{ &cg_lightningImpact, "cg_lightningImpact", "1", CVAR_ARCHIVE },
	{ &cg_lightningImpactCap, "cg_lightningImpactCap", "512", CVAR_ARCHIVE },
	{ &cg_drawTieredArmorAvailability, "cg_drawTieredArmorAvailability", "1", CVAR_ARCHIVE },
	{ &cg_armorTiered, "cg_armorTiered", "1", CVAR_ARCHIVE },
	{ &cg_drawFullWeaponBar, "cg_drawFullWeaponBar", "0", CVAR_ARCHIVE },
	{ &cg_weaponBar, "cg_weaponBar", "4", CVAR_ARCHIVE },
	{ &cg_weaponColor_grenade, "cg_weaponColor_grenade", DEFAULT_WEAPON_BAR_GRENADE_COLOR, CVAR_ARCHIVE },
	{ &cg_weaponConfig, "cg_weaponConfig", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_g, "cg_weaponConfig_g", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_mg, "cg_weaponConfig_mg", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_sg, "cg_weaponConfig_sg", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_gl, "cg_weaponConfig_gl", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_rl, "cg_weaponConfig_rl", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_lg, "cg_weaponConfig_lg", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_rg, "cg_weaponConfig_rg", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_pg, "cg_weaponConfig_pg", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_bfg, "cg_weaponConfig_bfg", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_gh, "cg_weaponConfig_gh", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_ng, "cg_weaponConfig_ng", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_pl, "cg_weaponConfig_pl", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_cg, "cg_weaponConfig_cg", "", CVAR_ARCHIVE },
	{ &cg_weaponConfig_hmg, "cg_weaponConfig_hmg", "", CVAR_ARCHIVE },
	{ &cg_weaponPrimary, "cg_weaponPrimary", "", CVAR_ROM },
	{ &cg_weaponPrimaryQueued, "cg_weaponPrimaryQueued", "", CVAR_TEMP },
	{ &cg_preferredStartingWeapons, "cg_preferredStartingWeapons", "", 0x00080801 },
	{ &cg_trueShotgun, "cg_trueShotgun", "0", 0x00081801 },
	{ &cg_trackPlayer, "cg_trackPlayer", "-1", CVAR_CHEAT },
	{ &cg_followKiller, "cg_followKiller", "0", CVAR_ARCHIVE },
	{ &cg_followPowerup, "cg_followPowerup", "0", CVAR_ARCHIVE },
	{ &cg_ignoreMouseInput, "cg_ignoreMouseInput", "0", CVAR_ARCHIVE },
	{ &cg_filter_angles, "cg_filter_angles", "0", CVAR_ARCHIVE },
	{ &cg_drawHitFriendTime, "cg_drawHitFriendTime", "5000", CVAR_ARCHIVE },
	{ &cg_drawDeadFriendTime, "cg_drawDeadFriendTime", "3000", CVAR_ARCHIVE },
	{ &cg_deadBodyDarken, "cg_deadBodyDarken", "1", CVAR_ARCHIVE },
	{ &cg_deadBodyColor, "cg_deadBodyColor", "0x333333ff", CVAR_ARCHIVE },
	{ &cg_speedometer, "cg_speedometer", "0", CVAR_ARCHIVE },
	{ &cg_specNames, "cg_specNames", "1", CVAR_ARCHIVE },
	{ &cg_specItemTimers, "cg_specItemTimers", "1", CVAR_ARCHIVE },
	{ &cg_specItemTimersX, "cg_specItemTimersX", "0", CVAR_ARCHIVE },
	{ &cg_specItemTimersY, "cg_specItemTimersY", "0", CVAR_ARCHIVE },
	{ &cg_specItemTimersSize, "cg_specItemTimersSize", "0.24", CVAR_ARCHIVE },
	{ &cg_specTeamVitals, "cg_specTeamVitals", "1", CVAR_ARCHIVE },
	{ &cg_specTeamVitalsHealthColor, "cg_specTeamVitalsHealthColor", "0", CVAR_ARCHIVE },
	{ &cg_itemTimers, "cg_itemTimers", "1", CVAR_ARCHIVE },
	{ &cg_screenDamage, "cg_screenDamage", DEFAULT_SCREEN_DAMAGE_COLOR, CVAR_ARCHIVE },
	{ &cg_screenDamage_Self, "cg_screenDamage_Self", DEFAULT_SCREEN_DAMAGE_SELF_COLOR, CVAR_ARCHIVE },
	{ &cg_screenDamage_Team, "cg_screenDamage_Team", DEFAULT_SCREEN_DAMAGE_TEAM_COLOR, CVAR_ARCHIVE },
	{ &cg_screenDamageAlpha, "cg_screenDamageAlpha", DEFAULT_SCREEN_DAMAGE_ALPHA, CVAR_ARCHIVE },
	{ &cg_screenDamageAlpha_Team, "cg_screenDamageAlpha_Team", DEFAULT_SCREEN_DAMAGE_ALPHA, CVAR_ARCHIVE },
	{ &cg_overheadNamesWidth, "cg_overheadNamesWidth", "120", CVAR_ARCHIVE },
	{ &cg_obituaryRowSize, "cg_obituaryRowSize", "5", CVAR_ARCHIVE },
	{ &cg_spectating, "cg_spectating", "0", CVAR_ROM },
	{ &cg_gametype, "cg_gametype", "0", CVAR_ROM },
	{ &cg_gameInfo1, "cg_gameInfo1", "", CVAR_ROM },
	{ &cg_gameInfo2, "cg_gameInfo2", "", CVAR_ROM },
	{ &cg_gameInfo3, "cg_gameInfo3", "", CVAR_ROM },
	{ &cg_gameInfo4, "cg_gameInfo4", "", CVAR_ROM },
	{ &cg_gameInfo5, "cg_gameInfo5", "", CVAR_ROM },
	{ &cg_gameInfo6, "cg_gameInfo6", "", CVAR_ROM },
	{ &cg_disableLoadout_g, "cg_disableLoadout_g", "0", CVAR_ROM },
	{ &cg_disableLoadout_mg, "cg_disableLoadout_mg", "0", CVAR_ROM },
	{ &cg_disableLoadout_sg, "cg_disableLoadout_sg", "0", CVAR_ROM },
	{ &cg_disableLoadout_gl, "cg_disableLoadout_gl", "0", CVAR_ROM },
	{ &cg_disableLoadout_rl, "cg_disableLoadout_rl", "0", CVAR_ROM },
	{ &cg_disableLoadout_lg, "cg_disableLoadout_lg", "0", CVAR_ROM },
	{ &cg_disableLoadout_rg, "cg_disableLoadout_rg", "0", CVAR_ROM },
	{ &cg_disableLoadout_pg, "cg_disableLoadout_pg", "0", CVAR_ROM },
	{ &cg_disableLoadout_bfg, "cg_disableLoadout_bfg", "0", CVAR_ROM },
	{ &cg_disableLoadout_gh, "cg_disableLoadout_gh", "0", CVAR_ROM },
	{ &cg_disableLoadout_ng, "cg_disableLoadout_ng", "0", CVAR_ROM },
	{ &cg_disableLoadout_pl, "cg_disableLoadout_pl", "0", CVAR_ROM },
	{ &cg_disableLoadout_cg, "cg_disableLoadout_cg", "0", CVAR_ROM },
	{ &cg_disableLoadout_hmg, "cg_disableLoadout_hmg", "0", CVAR_ROM },
	{ &cg_loadout, "cg_loadout", "0", CVAR_ROM }
//	{ &cg_pmove_fixed, "cg_pmove_fixed", "0", CVAR_USERINFO | CVAR_ARCHIVE }
};

#define DAMAGE_PLUM_WEAPON_BIT( weapon ) ( 1u << ( weapon ) )
#define DAMAGE_PLUM_ALL_WEAPONS_MASK ( \
	DAMAGE_PLUM_WEAPON_BIT( WP_GAUNTLET ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_MACHINEGUN ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_HEAVY_MACHINEGUN ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_SHOTGUN ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_GRENADE_LAUNCHER ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_ROCKET_LAUNCHER ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_LIGHTNING ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_RAILGUN ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_PLASMAGUN ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_BFG ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_GRAPPLING_HOOK ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_NAILGUN ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_PROX_LAUNCHER ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_CHAINGUN ) )
#define DAMAGE_PLUM_AOE_WEAPONS_MASK ( \
	DAMAGE_PLUM_WEAPON_BIT( WP_SHOTGUN ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_GRENADE_LAUNCHER ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_ROCKET_LAUNCHER ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_PLASMAGUN ) | \
	DAMAGE_PLUM_WEAPON_BIT( WP_BFG ) )

typedef struct damagePlumWeaponToken_s {
	const char		*token;
	weapon_t	weapon;
} damagePlumWeaponToken_t;

static const damagePlumWeaponToken_t damagePlumWeaponTokens[] = {
	{ "g", WP_GAUNTLET },
	{ "gauntlet", WP_GAUNTLET },
	{ "mg", WP_MACHINEGUN },
	{ "machinegun", WP_MACHINEGUN },
	{ "hmg", WP_HEAVY_MACHINEGUN },
	{ "heavy", WP_HEAVY_MACHINEGUN },
	{ "heavy_machinegun", WP_HEAVY_MACHINEGUN },
	{ "sg", WP_SHOTGUN },
	{ "shotgun", WP_SHOTGUN },
	{ "gl", WP_GRENADE_LAUNCHER },
	{ "grenade", WP_GRENADE_LAUNCHER },
	{ "grenadelauncher", WP_GRENADE_LAUNCHER },
	{ "rl", WP_ROCKET_LAUNCHER },
	{ "rocket", WP_ROCKET_LAUNCHER },
	{ "rocketlauncher", WP_ROCKET_LAUNCHER },
	{ "lg", WP_LIGHTNING },
	{ "lightning", WP_LIGHTNING },
	{ "rg", WP_RAILGUN },
	{ "rail", WP_RAILGUN },
	{ "railgun", WP_RAILGUN },
	{ "pg", WP_PLASMAGUN },
	{ "plasma", WP_PLASMAGUN },
	{ "plasmagun", WP_PLASMAGUN },
	{ "bfg", WP_BFG },
	{ "gh", WP_GRAPPLING_HOOK },
	{ "grapple", WP_GRAPPLING_HOOK },
	{ "hook", WP_GRAPPLING_HOOK },
	{ "cg", WP_CHAINGUN },
	{ "chaingun", WP_CHAINGUN },
	{ "ng", WP_NAILGUN },
	{ "nailgun", WP_NAILGUN },
	{ "pl", WP_PROX_LAUNCHER },
	{ "prox", WP_PROX_LAUNCHER },
	{ "proximity", WP_PROX_LAUNCHER },
	{ "proximitymine", WP_PROX_LAUNCHER }
};

/*
=============
CG_ParseDamagePlumWeaponValue

Parses the cg_damagePlum string into a weapon mask and preset.
=============
*/
static unsigned int CG_ParseDamagePlumWeaponValue( const char *value, damagePlumPreset_t *preset ) {
	char buffer[MAX_CVAR_VALUE_STRING];
	char token[MAX_TOKEN_CHARS];
	char *cursor;
	unsigned int mask;
	qboolean foundToken;
	int i;

	if ( !value || !*value || !Q_stricmp( value, "0" ) || !Q_stricmp( value, "off" ) || !Q_stricmp( value, "none" ) ) {
		*preset = DAMAGE_PLUM_PRESET_OFF;
		return 0u;
	}

	if ( !Q_stricmp( value, "1" ) || !Q_stricmp( value, "on" ) || !Q_stricmp( value, "all" ) ) {
		*preset = DAMAGE_PLUM_PRESET_ALL_WEAPONS;
		return DAMAGE_PLUM_ALL_WEAPONS_MASK;
	}

	if ( !Q_stricmp( value, "2" ) || !Q_stricmp( value, "aoe" ) ) {
		*preset = DAMAGE_PLUM_PRESET_AOE_WEAPONS;
		return DAMAGE_PLUM_AOE_WEAPONS_MASK;
	}

	Q_strncpyz( buffer, value, sizeof( buffer ) );
	cursor = buffer;
	mask = 0u;
	foundToken = qfalse;

	while ( *cursor ) {
		int length = 0;

		while ( *cursor && *cursor <= ' ' ) {
			cursor++;
		}

		if ( !*cursor ) {
			break;
		}

		while ( *cursor && *cursor > ' ' && length < MAX_TOKEN_CHARS - 1 ) {
			token[length++] = *cursor++;
		}
		token[length] = '\0';

		while ( *cursor && *cursor > ' ' ) {
			cursor++;
		}

		if ( !token[0] ) {
			continue;
		}

		if ( !Q_stricmp( token, "all" ) ) {
			*preset = DAMAGE_PLUM_PRESET_ALL_WEAPONS;
			return DAMAGE_PLUM_ALL_WEAPONS_MASK;
		}

		if ( !Q_stricmp( token, "aoe" ) ) {
			mask |= DAMAGE_PLUM_AOE_WEAPONS_MASK;
			foundToken = qtrue;
			continue;
		}

		for ( i = 0; i < (int)( sizeof( damagePlumWeaponTokens ) / sizeof( damagePlumWeaponTokens[0] ) ); i++ ) {
			if ( !Q_stricmp( token, damagePlumWeaponTokens[i].token ) ) {
				mask |= DAMAGE_PLUM_WEAPON_BIT( damagePlumWeaponTokens[i].weapon );
				foundToken = qtrue;
				break;
			}
		}
	}

	if ( !foundToken || mask == 0u ) {
		*preset = DAMAGE_PLUM_PRESET_OFF;
		return 0u;
	}

	if ( mask == DAMAGE_PLUM_ALL_WEAPONS_MASK ) {
		*preset = DAMAGE_PLUM_PRESET_ALL_WEAPONS;
		return mask;
	}

	if ( mask == DAMAGE_PLUM_AOE_WEAPONS_MASK ) {
		*preset = DAMAGE_PLUM_PRESET_AOE_WEAPONS;
		return mask;
	}

	*preset = DAMAGE_PLUM_PRESET_CUSTOM;
	return mask;
}

/*
=============
CG_ParseDamagePlumColorStyleValue

Normalizes the cg_damagePlumColorStyle value.
=============
*/
static damagePlumColorStyle_t CG_ParseDamagePlumColorStyleValue( int rawValue ) {
	switch ( rawValue ) {
	case DAMAGE_PLUM_COLOR_STYLE_DAMAGE:
		return DAMAGE_PLUM_COLOR_STYLE_DAMAGE;
	case DAMAGE_PLUM_COLOR_STYLE_WEAPON:
		return DAMAGE_PLUM_COLOR_STYLE_WEAPON;
	default:
		return DAMAGE_PLUM_COLOR_STYLE_MONOCHROME;
	}
}

/*
=============
CG_UpdateDamagePlumSettings

Refreshes the cached damage plum configuration.
=============
*/
static void CG_UpdateDamagePlumSettings( void ) {
	if ( damagePlumModificationCount != cg_damagePlum.modificationCount ) {
		damagePlumModificationCount = cg_damagePlum.modificationCount;
		cg.damagePlumWeaponBits = CG_ParseDamagePlumWeaponValue( cg_damagePlum.string, &cg.damagePlumPreset );
	}

	if ( damagePlumColorStyleModificationCount != cg_damagePlumColorStyle.modificationCount ) {
		damagePlumColorStyleModificationCount = cg_damagePlumColorStyle.modificationCount;
		cg.damagePlumColorStyle = CG_ParseDamagePlumColorStyleValue( cg_damagePlumColorStyle.integer );
	}
}


static int  cvarTableSize = sizeof( cvarTable ) / sizeof( cvarTable[0] );

static const vec4_t cg_defaultDeadBodyColor = { 51.0f / 255.0f, 51.0f / 255.0f, 51.0f / 255.0f, 1.0f };

/*
=============
CG_ParseDeadBodyHexDigit

Converts a hexadecimal character into an integer for corpse color parsing.
=============
*/
static int CG_ParseDeadBodyHexDigit( char ch ) {
	if ( ch >= '0' && ch <= '9' ) {
		return ch - '0';
	}
	if ( ch >= 'a' && ch <= 'f' ) {
		return 10 + ( ch - 'a' );
	}
	if ( ch >= 'A' && ch <= 'F' ) {
		return 10 + ( ch - 'A' );
	}
	return -1;
}

/*
=============
CG_ParseDeadBodyColor

Parses the configured corpse tint into a normalized RGBA vector.
=============
*/
static qboolean CG_ParseDeadBodyColor( const char *value, vec4_t color ) {
	char buffer[64];
	const char *hex;
	unsigned int raw;
	int len;
	int digit;
	int i;
	byte components[4];

	if ( !value || !*value ) {
		return qfalse;
	}
	Q_strncpyz( buffer, value, sizeof( buffer ) );
	hex = buffer;
	while ( *hex == ' ' || *hex == '	' || *hex == '"' ) {
		hex++;
	}
	if ( !Q_stricmp( hex, "NULL" ) ) {
		return qfalse;
	}
	if ( hex[0] == '0' && ( hex[1] == 'x' || hex[1] == 'X' ) ) {
		hex += 2;
	}
	len = strlen( hex );
	if ( len != 6 && len != 8 ) {
		return qfalse;
	}
	raw = 0;
	for ( i = 0 ; i < len ; i++ ) {
		digit = CG_ParseDeadBodyHexDigit( hex[i] );
		if ( digit < 0 ) {
			return qfalse;
		}
		raw = ( raw << 4 ) | digit;
	}
	if ( len == 6 ) {
		components[0] = ( raw >> 16 ) & 0xFF;
		components[1] = ( raw >> 8 ) & 0xFF;
		components[2] = raw & 0xFF;
		components[3] = 0xFF;
	} else {
		components[0] = ( raw >> 24 ) & 0xFF;
		components[1] = ( raw >> 16 ) & 0xFF;
		components[2] = ( raw >> 8 ) & 0xFF;
		components[3] = raw & 0xFF;
	}
	for ( i = 0 ; i < 4 ; i++ ) {
		color[i] = components[i] / 255.0f;
	}
	return qtrue;
}

/*
=============
CG_UpdateDeadBodyPalette

Synchronizes the cached corpse shading state with the latest cvars.
=============
*/
static void CG_UpdateDeadBodyPalette( void ) {
	cg.deadBodyDarken = (qboolean)( cg_deadBodyDarken.integer != 0 );
	if ( !CG_ParseDeadBodyColor( cg_deadBodyColor.string, cg.deadBodyColor ) ) {
		Vector4Copy( cg_defaultDeadBodyColor, cg.deadBodyColor );
	}
}

/*
=============
CG_ParseHexNibble

Converts a single hexadecimal digit to an integer value.
=============
*/
static int CG_ParseHexNibble( const char ch ) {
	if ( ch >= '0' && ch <= '9' ) {
		return ch - '0';
	}
	if ( ch >= 'a' && ch <= 'f' ) {
		return 10 + ch - 'a';
	}
	if ( ch >= 'A' && ch <= 'F' ) {
		return 10 + ch - 'A';
	}
	return -1;
}

/*
=============
CG_ParseWeaponBarColor

Parses a RRGGBBAA hex string into a normalized vec4_t.
=============
*/
static qboolean CG_ParseWeaponBarColor( const char *hex, vec4_t color ) {
	const char	*value;
	int		i;
	int		high;
	int		low;

	if ( !hex || !hex[0] ) {
		return qfalse;
	}

	value = hex;
	if ( !Q_stricmpn( value, "0x", 2 ) ) {
		value += 2;
	}

	if ( Q_strlen( value ) != 8 ) {
		return qfalse;
	}

	for ( i = 0; i < 4; i++ ) {
		high = CG_ParseHexNibble( value[i * 2] );
		low = CG_ParseHexNibble( value[i * 2 + 1] );

		if ( high < 0 || low < 0 ) {
			return qfalse;
		}

		color[i] = ( (float)( ( high << 4 ) | low ) ) / 255.0f;
	}

	return qtrue;
}

/*
=============
CG_UpdateWeaponBarGrenadeColor

Caches cg_weaponColor_grenade in cg.weaponBarGrenadeColor.
=============
*/
static void CG_UpdateWeaponBarGrenadeColor( void ) {
	vec4_t	parsedColor;

	if ( !CG_ParseWeaponBarColor( cg_weaponColor_grenade.string, parsedColor ) ) {
		CG_ParseWeaponBarColor( DEFAULT_WEAPON_BAR_GRENADE_COLOR, parsedColor );
	}

	Vector4Copy( parsedColor, cg.weaponBarGrenadeColor );
	weaponColorGrenadeModCount = cg_weaponColor_grenade.modificationCount;
}

/*
=============
CG_UpdateLowAmmoWarningPercentile

Caches cg_lowAmmoWarningPercentile for quick access.
=============
*/
static void CG_UpdateLowAmmoWarningPercentile( void ) {
	float	clamped;

	clamped = Com_Clamp( 0.0f, 1.0f, cg_lowAmmoWarningPercentile.value );
	cg.lowAmmoWarningPercentile = clamped;
	lowAmmoWarningPercentileModCount = cg_lowAmmoWarningPercentile.modificationCount;
}

/*
=============
CG_UpdateScreenDamageColorFromCvar

Parses a screen damage color customization string and caches the result.
=============
*/
static void CG_UpdateScreenDamageColorFromCvar( vmCvar_t *colorCvar, const char *defaultValue, vec4_t target, int *modificationCount ) {
	vec4_t	parsedColor;

	if ( !CG_ParseWeaponBarColor( colorCvar->string, parsedColor ) ) {
		CG_ParseWeaponBarColor( defaultValue, parsedColor );
	}

	Vector4Copy( parsedColor, target );
	*modificationCount = colorCvar->modificationCount;
}

/*
=============
CG_UpdateScreenDamageAlphaFromCvar

Caches the scalar alpha intensity used by screen damage effects.
=============
*/
static void CG_UpdateScreenDamageAlphaFromCvar( vmCvar_t *alphaCvar, float *target, int *modificationCount ) {
	float	clamped;

	clamped = Com_Clamp( 0.0f, 200.0f, alphaCvar->value );
	*target = clamped;
	*modificationCount = alphaCvar->modificationCount;
}

/*
=================
CG_RegisterCvars
=================
*/
void CG_RegisterCvars( void ) {
	int			i;
	cvarTable_t	*cv;
	qboolean	refreshClients;
	char		var[MAX_TOKEN_CHARS];

	for ( i = 0, cv = cvarTable ; i < cvarTableSize ; i++, cv++ ) {
		trap_Cvar_Register( cv->vmCvar, cv->cvarName,
			cv->defaultString, cv->cvarFlags );
	}

	// see if we are also running the server on this machine
	trap_Cvar_VariableStringBuffer( "sv_running", var, sizeof( var ) );
	cgs.localServer = atoi( var );

	forceModelModificationCount = cg_forceModel.modificationCount;
	forceTeamModelModificationCount = cg_forceTeamModel.modificationCount;
	forceTeamSkinModificationCount = cg_forceTeamSkin.modificationCount;
	forceEnemyModelModificationCount = cg_forceEnemyModel.modificationCount;
	forceEnemySkinModificationCount = cg_forceEnemySkin.modificationCount;
	forceTeamWeaponColorModificationCount = cg_forceTeamWeaponColor.modificationCount;
	forceEnemyWeaponColorModificationCount = cg_forceEnemyWeaponColor.modificationCount;
	teamHeadColorModificationCount = cg_teamHeadColor.modificationCount;
	teamUpperColorModificationCount = cg_teamUpperColor.modificationCount;
	teamLowerColorModificationCount = cg_teamLowerColor.modificationCount;
	enemyHeadColorModificationCount = cg_enemyHeadColor.modificationCount;
	enemyUpperColorModificationCount = cg_enemyUpperColor.modificationCount;
	enemyLowerColorModificationCount = cg_enemyLowerColor.modificationCount;
	deadBodyDarkenModificationCount = cg_deadBodyDarken.modificationCount;
	deadBodyColorModificationCount = cg_deadBodyColor.modificationCount;

	CG_UpdateDeadBodyPalette();
	armorTieredModificationCount = cg_armorTiered.modificationCount;
	vignetteModificationCount = cg_vignette.modificationCount;
	voiceChatIndicatorModificationCount = cg_voiceChatIndicator.modificationCount;

	cg.armorTieredEnabled = (qboolean)( cg_armorTiered.integer != 0 );
	cg.vignetteEnabled = (qboolean)( cg_vignette.integer != 0 );
	cg.voiceChatIndicatorEnabled = (qboolean)( cg_voiceChatIndicator.integer != 0 );

	cg.kickScale = cg_kickScale.value;
	if ( cg.kickScale < 0.0f ) {
		cg.kickScale = 0.0f;
	}

	cg.bobScale = cg_bob.value;
	if ( cg.bobScale < 0.0f ) {
		cg.bobScale = 0.0f;
	}

	CG_UpdateDamagePlumSettings();
	CG_UpdateSimpleItemsSettings();
	CG_UpdateWeaponBarGrenadeColor();
	CG_UpdateLowAmmoWarningPercentile();
	CG_UpdateCrosshairColorSettings();
	CG_UpdateCrosshairPulseSettings();
	CG_UpdateCrosshairHitSettings();
	CG_UpdateScreenDamageColorFromCvar( &cg_screenDamage, DEFAULT_SCREEN_DAMAGE_COLOR, cg.screenDamageColor, &screenDamageColorModificationCount );
	CG_UpdateScreenDamageColorFromCvar( &cg_screenDamage_Self, DEFAULT_SCREEN_DAMAGE_SELF_COLOR, cg.screenDamageSelfColor, &screenDamageSelfColorModificationCount );
	CG_UpdateScreenDamageColorFromCvar( &cg_screenDamage_Team, DEFAULT_SCREEN_DAMAGE_TEAM_COLOR, cg.screenDamageTeamColor, &screenDamageTeamColorModificationCount );
	CG_UpdateScreenDamageAlphaFromCvar( &cg_screenDamageAlpha, &cg.screenDamageAlpha, &screenDamageAlphaModificationCount );
	CG_UpdateScreenDamageAlphaFromCvar( &cg_screenDamageAlpha_Team, &cg.screenDamageAlphaTeam, &screenDamageAlphaTeamModificationCount );
	CG_UpdateAutomationSettings();

	trap_Cvar_Register(NULL, "model", DEFAULT_MODEL, CVAR_USERINFO | CVAR_ARCHIVE );
	trap_Cvar_Register(NULL, "headmodel", DEFAULT_MODEL, CVAR_USERINFO | CVAR_ARCHIVE );
	trap_Cvar_Register(NULL, "team_model", DEFAULT_TEAM_MODEL, CVAR_USERINFO | CVAR_ARCHIVE );
	trap_Cvar_Register(NULL, "team_headmodel", DEFAULT_TEAM_HEAD, CVAR_USERINFO | CVAR_ARCHIVE );

	announcerModificationCount = cg_announcer.modificationCount;
}

/*																																			
===================
CG_ForceModelChange
===================
*/
static void CG_ForceModelChange( void ) {
	int		i;

	for (i=0 ; i<MAX_CLIENTS ; i++) {
		const char		*clientInfo;

		clientInfo = CG_ConfigString( CS_PLAYERS+i );
		if ( !clientInfo[0] ) {
			continue;
		}
		CG_NewClientInfo( i );
	}
}

/*
=============
CG_UpdateSimpleItemsSettings

Synchronize cached simple item settings with their cvars.
=============
*/
static void CG_UpdateSimpleItemsSettings( void ) {
	if ( simpleItemsHeightOffsetModificationCount != cg_simpleItemsHeightOffset.modificationCount ) {
		simpleItemsHeightOffsetModificationCount = cg_simpleItemsHeightOffset.modificationCount;
		cg.simpleItemsHeightOffset = cg_simpleItemsHeightOffset.value;
	}

	if ( simpleItemsBobModificationCount != cg_simpleItemsBob.modificationCount ) {
		simpleItemsBobModificationCount = cg_simpleItemsBob.modificationCount;
		cg.simpleItemsBob = cg_simpleItemsBob.value;
		if ( cg.simpleItemsBob < 0.0f ) {
			cg.simpleItemsBob = 0.0f;
		}
	}

	if ( simpleItemsRadiusModificationCount != cg_simpleItemsRadius.modificationCount ) {
		simpleItemsRadiusModificationCount = cg_simpleItemsRadius.modificationCount;
		cg.simpleItemsRadius = cg_simpleItemsRadius.value;
		if ( cg.simpleItemsRadius < 0.0f ) {
			cg.simpleItemsRadius = 0.0f;
		}
	}
}

/*
=============
CG_UpdateAutomationSettings

Caches movement, projectile, and prediction automation preferences.
=============
*/
static void CG_UpdateAutomationSettings( void ) {
	float	clampedNudge;

	cg.autoHopEnabled = (qboolean)( cg_autoHop.integer != 0 );
	cg.autoProjectileNudgeEnabled = (qboolean)( cg_autoProjectileNudge.integer != 0 );

	clampedNudge = cg_projectileNudge.value;
	if ( clampedNudge < 0.0f ) {
		clampedNudge = 0.0f;
	}

	cg.projectileNudgeAmount = clampedNudge;
	cg.projectileNudgeOffset = clampedNudge;
	cg.projectileNudgeActive = (qboolean)( cg.autoProjectileNudgeEnabled || ( clampedNudge > 0.0f ) );
	cg.predictLocalRailshots = (qboolean)( cg_predictLocalRailshots.integer != 0 );
	cg.autoActionFlags = cg_autoAction.integer;
}

/*
=============
CG_ClearAutomationState

Resets cached automation state so stale preferences never leak between games.
=============
*/
static void CG_ClearAutomationState( void ) {
	cg.autoHopEnabled = qfalse;
	cg.autoProjectileNudgeEnabled = qfalse;
	cg.projectileNudgeActive = qfalse;
	cg.projectileNudgeAmount = 0.0f;
	cg.projectileNudgeOffset = 0.0f;
	cg.predictLocalRailshots = qfalse;
	cg.autoActionFlags = 0;
	cg.autoActionFired = qfalse;
	cg.autoActionScreenshotQueued = qfalse;
	cg.autoActionStatsQueued = qfalse;
	cg.autoActionScreenshotTime = 0;
	cg.autoActionStatsTime = 0;
	cg.autoActionDemoIndex = 0;
}

/*
=============
CG_HandleAutoActionsIntermission

Dispatches cg_autoAction console commands after entering intermission.
=============
*/
void CG_HandleAutoActionsIntermission( const playerState_t *ps ) {
	char		demoName[MAX_QPATH];
	int		flags;

	if ( cg.demoPlayback ) {
		return;
	}

	if ( !ps || ps->persistant[PERS_TEAM] == TEAM_SPECTATOR ) {
		return;
	}

	if ( cg.autoActionFired ) {
		return;
	}

	flags = cg.autoActionFlags;
	if ( flags == 0 ) {
		return;
	}

	cg.autoActionFired = qtrue;
	cg.autoActionScreenshotQueued = qfalse;
	cg.autoActionStatsQueued = qfalse;

	if ( flags & CG_AUTOACTION_DEMO_RECORD ) {
		trap_SendConsoleCommand( "stoprecord; wait\n" );
		Com_sprintf( demoName, sizeof( demoName ), "auto%03i", cg.autoActionDemoIndex );
		cg.autoActionDemoIndex = ( cg.autoActionDemoIndex + 1 ) % CG_AUTOACTION_MAX_RECORDINGS;
		trap_SendConsoleCommand( va( "record \"%s\"\n", demoName ) );
	}

	if ( flags & CG_AUTOACTION_SCREENSHOT ) {
		cg.autoActionScreenshotQueued = qtrue;
		cg.autoActionScreenshotTime = cg.time + CG_AUTOACTION_SCREENSHOT_DELAY;
	}

	if ( flags & CG_AUTOACTION_STATS_UPLOAD ) {
		cg.autoActionStatsQueued = qtrue;
		cg.autoActionStatsTime = cg.time + CG_AUTOACTION_STATS_DELAY;
	}
}

/*
=============
CG_RunQueuedAutoActions

Executes delayed screenshot and stat commands tied to cg_autoAction.
=============
*/
void CG_RunQueuedAutoActions( void ) {
	if ( cg.demoPlayback ) {
		cg.autoActionScreenshotQueued = qfalse;
		cg.autoActionStatsQueued = qfalse;
		return;
	}

	if ( cg.autoActionScreenshotQueued && cg.time >= cg.autoActionScreenshotTime ) {
		cg.autoActionScreenshotQueued = qfalse;
		trap_SendConsoleCommand( "screenshotJPEG scoreboard\n" );
	}

	if ( cg.autoActionStatsQueued && cg.time >= cg.autoActionStatsTime ) {
		cg.autoActionStatsQueued = qfalse;
		trap_SendConsoleCommand( "pstats\n" );
	}
}

#define QL_CROSSHAIR_COLOR_COUNT	27

static const vec3_t cg_crosshairPalette[QL_CROSSHAIR_COLOR_COUNT] = {
	{ 1.00f, 1.00f, 1.00f },
	{ 1.00f, 1.00f, 1.00f },
	{ 0.90f, 0.90f, 0.90f },
	{ 0.75f, 0.75f, 0.75f },
	{ 0.50f, 0.50f, 0.50f },
	{ 0.25f, 0.25f, 0.25f },
	{ 0.00f, 0.00f, 0.00f },
	{ 1.00f, 0.35f, 0.35f },
	{ 1.00f, 0.00f, 0.00f },
	{ 0.70f, 0.00f, 0.00f },
	{ 1.00f, 0.55f, 0.00f },
	{ 1.00f, 0.80f, 0.00f },
	{ 1.00f, 1.00f, 0.00f },
	{ 0.80f, 1.00f, 0.00f },
	{ 0.55f, 1.00f, 0.00f },
	{ 0.00f, 1.00f, 0.00f },
	{ 0.00f, 1.00f, 0.55f },
	{ 0.00f, 1.00f, 0.80f },
	{ 0.00f, 1.00f, 1.00f },
	{ 0.00f, 0.80f, 1.00f },
	{ 0.00f, 0.55f, 1.00f },
	{ 0.00f, 0.00f, 1.00f },
	{ 0.35f, 0.00f, 1.00f },
	{ 0.55f, 0.00f, 1.00f },
	{ 0.80f, 0.00f, 1.00f },
	{ 1.00f, 0.00f, 1.00f },
	{ 1.00f, 0.00f, 0.55f }
};

/*
=============
CG_CrosshairHexCharToInt

Converts a hexadecimal character for crosshair color parsing.
=============
*/
static int CG_CrosshairHexCharToInt( char ch ) {
	if ( ch >= '0' && ch <= '9' ) {
		return ch - '0';
	}
	if ( ch >= 'a' && ch <= 'f' ) {
		return 10 + ( ch - 'a' );
	}
	if ( ch >= 'A' && ch <= 'F' ) {
		return 10 + ( ch - 'A' );
	}
	return -1;
}

/*
=============
CG_ParseCrosshairColorString

Attempts to parse a custom crosshair color string into a vec4_t.
=============
*/
static qboolean CG_ParseCrosshairColorString( const char *value, vec4_t color ) {
	char		buffer[64];
	const char	*hex;
	unsigned int raw;
	int		len;
	int		digit;
	int		i;

	if ( !value || !*value ) {
		return qfalse;
	}
	Q_strncpyz( buffer, value, sizeof( buffer ) );
	hex = buffer;
	while ( *hex == ' ' || *hex == '\t' || *hex == '"' ) {
		hex++;
	}
	if ( !Q_stricmp( hex, "NULL" ) ) {
		return qfalse;
	}
	if ( hex[0] == '0' && ( hex[1] == 'x' || hex[1] == 'X' ) ) {
		hex += 2;
	} else if ( hex[0] == '#' ) {
		hex++;
	}
	len = strlen( hex );
	if ( len != 6 && len != 8 ) {
		return qfalse;
	}
	raw = 0u;
	for ( i = 0 ; i < len ; i++ ) {
		digit = CG_CrosshairHexCharToInt( hex[i] );
		if ( digit < 0 ) {
			return qfalse;
		}
		raw = ( raw << 4 ) | (unsigned int)digit;
	}
	if ( len == 6 ) {
		color[0] = ( ( raw >> 16 ) & 0xFF ) / 255.0f;
		color[1] = ( ( raw >> 8 ) & 0xFF ) / 255.0f;
		color[2] = ( raw & 0xFF ) / 255.0f;
		color[3] = 1.0f;
	} else {
		color[0] = ( ( raw >> 24 ) & 0xFF ) / 255.0f;
		color[1] = ( ( raw >> 16 ) & 0xFF ) / 255.0f;
		color[2] = ( ( raw >> 8 ) & 0xFF ) / 255.0f;
		color[3] = ( raw & 0xFF ) / 255.0f;
	}
	return qtrue;
}

/*
=============
CG_SetCrosshairColorFromIndex

Populates a color vector using a palette-backed crosshair index.
=============
*/
static void CG_SetCrosshairColorFromIndex( int index, vec4_t color ) {
	if ( index < 1 || index >= QL_CROSSHAIR_COLOR_COUNT ) {
		index = 1;
	}
	VectorCopy( cg_crosshairPalette[index], color );
	color[3] = 1.0f;
}

/*
=============
CG_UpdateCrosshairColorSettings

Synchronizes cached crosshair color information with user settings.
=============
*/
static void CG_UpdateCrosshairColorSettings( void ) {
	vec4_t	baseColor;
	float	brightness;
	int	i;

	if ( crosshairColorModificationCount == cg_crosshairColor.modificationCount &&
		crosshairBrightnessModificationCount == cg_crosshairBrightness.modificationCount ) {
		return;
	}
	if ( !CG_ParseCrosshairColorString( cg_crosshairColor.string, baseColor ) ) {
		CG_SetCrosshairColorFromIndex( cg_crosshairColor.integer, baseColor );
	}
	brightness = Com_Clamp( 0.0f, 2.0f, cg_crosshairBrightness.value );
	for ( i = 0 ; i < 3 ; i++ ) {
		cg.crosshairColor[i] = Com_Clamp( 0.0f, 1.0f, baseColor[i] * brightness );
	}
	cg.crosshairColor[3] = Com_Clamp( 0.0f, 1.0f, brightness );
	crosshairColorModificationCount = cg_crosshairColor.modificationCount;
	crosshairBrightnessModificationCount = cg_crosshairBrightness.modificationCount;
}

/*
=============
CG_UpdateCrosshairPulseSettings

Caches the boolean used to control the pickup crosshair pulse.
=============
*/
static void CG_UpdateCrosshairPulseSettings( void ) {
	if ( crosshairPulseModificationCount == cg_crosshairPulse.modificationCount ) {
		return;
	}
	cg.crosshairPulseEnabled = (qboolean)( cg_crosshairPulse.integer != 0 );
	crosshairPulseModificationCount = cg_crosshairPulse.modificationCount;
}

/*
=============
CG_UpdateCrosshairHitSettings

Synchronizes hit indicator timing, style, and color caches.
=============
*/
static void CG_UpdateCrosshairHitSettings( void ) {
	vec4_t	baseColor;
	int		clampedTime;

	if ( crosshairHitStyleModificationCount != cg_crosshairHitStyle.modificationCount ) {
		cg.crosshairHitStyle = cg_crosshairHitStyle.integer;
		crosshairHitStyleModificationCount = cg_crosshairHitStyle.modificationCount;
	}
	if ( crosshairHitTimeModificationCount != cg_crosshairHitTime.modificationCount ) {
		clampedTime = cg_crosshairHitTime.integer;
		if ( clampedTime < 0 ) {
			clampedTime = 0;
		}
		if ( clampedTime > 2000 ) {
			clampedTime = 2000;
		}
		cg.crosshairHitTime = clampedTime;
		crosshairHitTimeModificationCount = cg_crosshairHitTime.modificationCount;
	}
	if ( crosshairHitColorModificationCount != cg_crosshairHitColor.modificationCount ) {
		if ( !CG_ParseCrosshairColorString( cg_crosshairHitColor.string, baseColor ) ) {
			CG_SetCrosshairColorFromIndex( cg_crosshairHitColor.integer, baseColor );
		}
		VectorCopy( baseColor, cg.crosshairHitColor );
		crosshairHitColorModificationCount = cg_crosshairHitColor.modificationCount;
	}
}


/*
=================
CG_UpdateCvars
=================
*/
void CG_UpdateCvars( void ) {
	int			i;
	cvarTable_t	*cv;
	qboolean	refreshClients;
	qboolean	refreshDeadBodyPalette;

	for ( i = 0, cv = cvarTable ; i < cvarTableSize ; i++, cv++ ) {
		trap_Cvar_Update( cv->vmCvar );
	}

	// check for modications here

	// If team overlay is on, ask for updates from the server.  If its off,
	// let the server know so we don't receive it
	if ( drawTeamOverlayModificationCount != cg_drawTeamOverlay.modificationCount ) {
		drawTeamOverlayModificationCount = cg_drawTeamOverlay.modificationCount;

		if ( cg_drawTeamOverlay.integer > 0 ) {
			trap_Cvar_Set( "teamoverlay", "1" );
		} else {
			trap_Cvar_Set( "teamoverlay", "0" );
		}
		// FIXME E3 HACK
		trap_Cvar_Set( "teamoverlay", "1" );
	}

	refreshClients = qfalse;
	refreshDeadBodyPalette = qfalse;

	if ( forceModelModificationCount != cg_forceModel.modificationCount ) {
		forceModelModificationCount = cg_forceModel.modificationCount;
		refreshClients = qtrue;
	}
	if ( forceTeamModelModificationCount != cg_forceTeamModel.modificationCount ) {
		forceTeamModelModificationCount = cg_forceTeamModel.modificationCount;
		refreshClients = qtrue;
	}
	if ( forceTeamSkinModificationCount != cg_forceTeamSkin.modificationCount ) {
		forceTeamSkinModificationCount = cg_forceTeamSkin.modificationCount;
		refreshClients = qtrue;
	}
	if ( forceEnemyModelModificationCount != cg_forceEnemyModel.modificationCount ) {
		forceEnemyModelModificationCount = cg_forceEnemyModel.modificationCount;
		refreshClients = qtrue;
	}
	if ( forceEnemySkinModificationCount != cg_forceEnemySkin.modificationCount ) {
		forceEnemySkinModificationCount = cg_forceEnemySkin.modificationCount;
		refreshClients = qtrue;
	}
	if ( forceTeamWeaponColorModificationCount != cg_forceTeamWeaponColor.modificationCount ) {
		forceTeamWeaponColorModificationCount = cg_forceTeamWeaponColor.modificationCount;
		refreshClients = qtrue;
	}
	if ( forceEnemyWeaponColorModificationCount != cg_forceEnemyWeaponColor.modificationCount ) {
		forceEnemyWeaponColorModificationCount = cg_forceEnemyWeaponColor.modificationCount;
		refreshClients = qtrue;
	}
	if ( teamHeadColorModificationCount != cg_teamHeadColor.modificationCount ) {
		teamHeadColorModificationCount = cg_teamHeadColor.modificationCount;
		refreshClients = qtrue;
	}
	if ( teamUpperColorModificationCount != cg_teamUpperColor.modificationCount ) {
		teamUpperColorModificationCount = cg_teamUpperColor.modificationCount;
		refreshClients = qtrue;
	}
	if ( teamLowerColorModificationCount != cg_teamLowerColor.modificationCount ) {
		teamLowerColorModificationCount = cg_teamLowerColor.modificationCount;
		refreshClients = qtrue;
	}
	if ( enemyHeadColorModificationCount != cg_enemyHeadColor.modificationCount ) {
		enemyHeadColorModificationCount = cg_enemyHeadColor.modificationCount;
		refreshClients = qtrue;
	}
	if ( enemyUpperColorModificationCount != cg_enemyUpperColor.modificationCount ) {
		enemyUpperColorModificationCount = cg_enemyUpperColor.modificationCount;
		refreshClients = qtrue;
	}
	if ( enemyLowerColorModificationCount != cg_enemyLowerColor.modificationCount ) {
		enemyLowerColorModificationCount = cg_enemyLowerColor.modificationCount;
		refreshClients = qtrue;
	}
	if ( deadBodyDarkenModificationCount != cg_deadBodyDarken.modificationCount ) {
		deadBodyDarkenModificationCount = cg_deadBodyDarken.modificationCount;
		refreshDeadBodyPalette = qtrue;
	}
	if ( deadBodyColorModificationCount != cg_deadBodyColor.modificationCount ) {
		deadBodyColorModificationCount = cg_deadBodyColor.modificationCount;
		refreshDeadBodyPalette = qtrue;
  }
	if ( armorTieredModificationCount != cg_armorTiered.modificationCount ) {
		armorTieredModificationCount = cg_armorTiered.modificationCount;
		cg.armorTieredEnabled = (qboolean)( cg_armorTiered.integer != 0 );
	}
	if ( vignetteModificationCount != cg_vignette.modificationCount ) {
		vignetteModificationCount = cg_vignette.modificationCount;
		cg.vignetteEnabled = (qboolean)( cg_vignette.integer != 0 );
	}
	if ( voiceChatIndicatorModificationCount != cg_voiceChatIndicator.modificationCount ) {
		voiceChatIndicatorModificationCount = cg_voiceChatIndicator.modificationCount;
		cg.voiceChatIndicatorEnabled = (qboolean)( cg_voiceChatIndicator.integer != 0 );
	}

	if ( refreshClients ) {
		CG_ForceModelChange();
	}
	if ( refreshDeadBodyPalette ) {
		CG_UpdateDeadBodyPalette();
	}


	cg.kickScale = cg_kickScale.value;
	if ( cg.kickScale < 0.0f ) {
		cg.kickScale = 0.0f;
	}

	cg.bobScale = cg_bob.value;
	if ( cg.bobScale < 0.0f ) {
		cg.bobScale = 0.0f;
	}
	if ( weaponColorGrenadeModCount != cg_weaponColor_grenade.modificationCount ) {
		CG_UpdateWeaponBarGrenadeColor();
	}
	if ( lowAmmoWarningPercentileModCount != cg_lowAmmoWarningPercentile.modificationCount ) {
		CG_UpdateLowAmmoWarningPercentile();
	}
	if ( screenDamageColorModificationCount != cg_screenDamage.modificationCount ) {
		CG_UpdateScreenDamageColorFromCvar( &cg_screenDamage, DEFAULT_SCREEN_DAMAGE_COLOR, cg.screenDamageColor, &screenDamageColorModificationCount );
	}
	if ( screenDamageSelfColorModificationCount != cg_screenDamage_Self.modificationCount ) {
		CG_UpdateScreenDamageColorFromCvar( &cg_screenDamage_Self, DEFAULT_SCREEN_DAMAGE_SELF_COLOR, cg.screenDamageSelfColor, &screenDamageSelfColorModificationCount );
	}
	if ( screenDamageTeamColorModificationCount != cg_screenDamage_Team.modificationCount ) {
		CG_UpdateScreenDamageColorFromCvar( &cg_screenDamage_Team, DEFAULT_SCREEN_DAMAGE_TEAM_COLOR, cg.screenDamageTeamColor, &screenDamageTeamColorModificationCount );
	}
	if ( screenDamageAlphaModificationCount != cg_screenDamageAlpha.modificationCount ) {
		CG_UpdateScreenDamageAlphaFromCvar( &cg_screenDamageAlpha, &cg.screenDamageAlpha, &screenDamageAlphaModificationCount );
	}
	if ( screenDamageAlphaTeamModificationCount != cg_screenDamageAlpha_Team.modificationCount ) {
		CG_UpdateScreenDamageAlphaFromCvar( &cg_screenDamageAlpha_Team, &cg.screenDamageAlphaTeam, &screenDamageAlphaTeamModificationCount );
	}
	cg.zoomToggle = (qboolean)( cg_zoomToggle.integer != 0 );
cg.zoomOutOnDeath = (qboolean)( cg_zoomOutOnDeath.integer != 0 );
CG_UpdateDamagePlumSettings();

	CG_UpdateSimpleItemsSettings();
	CG_UpdateCrosshairColorSettings();
	CG_UpdateCrosshairPulseSettings();
	CG_UpdateCrosshairHitSettings();
	if ( announcerModificationCount != cg_announcer.modificationCount ) {
		announcerModificationCount = cg_announcer.modificationCount;
		CG_UpdateAnnouncerProfileFromCvar( qfalse );
	}
}

/*
=============
CG_GetChatHistoryLength

Calculates the bounded chat history length using cg_chatHistoryLength,
falling back to cg_teamChatHeight when the new cvar isn't configured.
=============
*/
int CG_GetChatHistoryLength( void ) {
	int historyLength;

	historyLength = cg_chatHistoryLength.integer;
	if ( historyLength <= 0 ) {
		historyLength = cg_teamChatHeight.integer;
	}
	if ( historyLength <= 0 ) {
		historyLength = TEAMCHAT_HEIGHT;
	}
	if ( historyLength > TEAMCHAT_HEIGHT ) {
		historyLength = TEAMCHAT_HEIGHT;
	}

	return historyLength;
}

/*
=============
CG_ParseLastMessageValue

Parses the persisted last message payload into its timestamp and body.
=============
*/
static qboolean CG_ParseLastMessageValue( const char *value, int *timestamp, char *message, int messageSize ) {
	const char		*cursor;
	int			parsed;
	int			sign;

	if ( !value || !*value || !message || messageSize <= 0 ) {
		return qfalse;
	}

	cursor = value;
	sign = 1;
	if ( *cursor == '-' ) {
		sign = -1;
		cursor++;
	} else if ( *cursor == '+' ) {
		cursor++;
	}

	if ( *cursor < '0' || *cursor > '9' ) {
		return qfalse;
	}

	parsed = 0;
	while ( *cursor >= '0' && *cursor <= '9' ) {
		parsed = ( parsed * 10 ) + ( *cursor - '0' );
		cursor++;
	}
	parsed *= sign;

	while ( *cursor == ' ' || *cursor == '\t' ) {
		cursor++;
	}

	Q_strncpyz( message, cursor, messageSize );
	if ( timestamp ) {
		*timestamp = parsed;
	}

	return qtrue;
}

/*
=============
CG_WriteLastMessageCvar

Persists the latest last message data into cg_lastmsg for UI consumers.
=============
*/
static void CG_WriteLastMessageCvar( int timestamp, const char *message ) {
	char	buffer[MAX_STRING_CHARS];

	if ( !message ) {
		message = "";
	}

	Com_sprintf( buffer, sizeof( buffer ), "%i %s", timestamp, message );
	trap_Cvar_Set( "cg_lastmsg", buffer );
	trap_Cvar_Update( &cg_lastmsg );
}

/*
=============
CG_ReplayLastMessageFromCvar

Restores the persisted last message into the HUD print stack when initializing.
=============
*/
static void CG_ReplayLastMessageFromCvar( void ) {
	char	storedValue[MAX_STRING_CHARS];
	char	message[MAX_STRING_CHARS];
	int		storedTime;

	trap_Cvar_VariableStringBuffer( "cg_lastmsg", storedValue, sizeof( storedValue ) );
	if ( !CG_ParseLastMessageValue( storedValue, &storedTime, message, sizeof( message ) ) ) {
		return;
	}

	if ( message[0] ) {
		CG_SetPrintString( SYSTEM_PRINT, message );
	}

	CG_WriteLastMessageCvar( cg.time, message );
}

/*
=============
CG_ShouldDisplayVoiceIndicator

Returns whether voice chat indicators should be drawn.
*/
qboolean CG_ShouldDisplayVoiceIndicator( void ) {
	if ( !cg.voiceChatIndicatorEnabled ) {
		return qfalse;
	}
	if ( !cg_playVoiceChats.integer && !cg_showVoiceText.integer ) {
		return qfalse;
	}
	return qtrue;
}

int CG_CrosshairPlayer( void ) {
if ( cg.time > ( cg.crosshairClientTime + 1000 ) ) {
		return -1;
	}
	return cg.crosshairClientNum;
}

int CG_LastAttacker( void ) {
	if ( !cg.attackerTime ) {
		return -1;
	}
	return cg.snap->ps.persistant[PERS_ATTACKER];
}

void QDECL CG_Printf( const char *msg, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, msg);
	vsprintf (text, msg, argptr);
	va_end (argptr);

	trap_Print( text );
	if ( cg_chatbeep.integer && cgs.media.talkSound ) {
		trap_S_StartLocalSound( cgs.media.talkSound, CHAN_LOCAL_SOUND );
	}
}

void QDECL CG_Error( const char *msg, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, msg);
	vsprintf (text, msg, argptr);
	va_end (argptr);

	trap_Error( text );
}

#ifndef CGAME_HARD_LINKED
// this is only here so the functions in q_shared.c and bg_*.c can link (FIXME)

void QDECL Com_Error( int level, const char *error, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, error);
	vsprintf (text, error, argptr);
	va_end (argptr);

	CG_Error( "%s", text);
}

void QDECL Com_Printf( const char *msg, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start (argptr, msg);
	vsprintf (text, msg, argptr);
	va_end (argptr);

	CG_Printf ("%s", text);
}

#endif

/*
================
CG_Argv
================
*/
const char *CG_Argv( int arg ) {
	static char	buffer[MAX_STRING_CHARS];

	trap_Argv( arg, buffer, sizeof( buffer ) );

	return buffer;
}


//========================================================================

/*
=================
CG_RegisterItemSounds

The server says this item is used on this level
=================
*/
static void CG_RegisterItemSounds( int itemNum ) {
	gitem_t			*item;
	char			data[MAX_QPATH];
	char			*s, *start;
	int				len;

	item = &bg_itemlist[ itemNum ];

	if( item->pickup_sound ) {
		trap_S_RegisterSound( item->pickup_sound, qfalse );
	}

	// parse the space seperated precache string for other media
	s = item->sounds;
	if (!s || !s[0])
		return;

	while (*s) {
		start = s;
		while (*s && *s != ' ') {
			s++;
		}

		len = s-start;
		if (len >= MAX_QPATH || len < 5) {
			CG_Error( "PrecacheItem: %s has bad precache string", 
				item->classname);
			return;
		}
		memcpy (data, start, len);
		data[len] = 0;
		if ( *s ) {
			s++;
		}

		if ( !strcmp(data+len-3, "wav" )) {
			trap_S_RegisterSound( data, qfalse );
		}
	}
}



/*
============
CG_RegisterAnnouncerClip

Registers an announcer clip, falling back to the default voice set when needed.
============
*/
static sfxHandle_t CG_RegisterAnnouncerClip( const char *folder, const char *sample ) {
	static const char *const exts[] = { ".ogg", ".wav" };
	char		path[MAX_QPATH];
	sfxHandle_t	sfx;
	int		i;

	if ( folder && *folder ) {
		for ( i = 0; i < 2; i++ ) {
			Com_sprintf( path, sizeof( path ), "sound/announcer/%s/%s%s", folder, sample, exts[i] );
			sfx = trap_S_RegisterSound( path, qtrue );
			if ( sfx ) {
				return sfx;
			}
		}
	}

	for ( i = 0; i < 2; i++ ) {
		Com_sprintf( path, sizeof( path ), "sound/feedback/%s%s", sample, exts[i] );
		sfx = trap_S_RegisterSound( path, qtrue );
		if ( sfx ) {
			return sfx;
		}
	}

	return 0;
}

/*
============
CG_RegisterAnnouncerVoiceSet

Caches the announcer warning clips for a specific profile.
============
*/
static void CG_RegisterAnnouncerVoiceSet( cgAnnouncerProfile_t profile, const char *folder ) {
	cgAnnouncerSoundSet_t	*set;

	if ( profile <= ANNOUNCER_PROFILE_DISABLED || profile >= ANNOUNCER_PROFILE_COUNT ) {
		return;
	}

	set = &cgs.media.announcerSoundSets[profile];
	set->oneMinute = CG_RegisterAnnouncerClip( folder, "1_minute" );
	set->fiveMinute = CG_RegisterAnnouncerClip( folder, "5_minute" );
	set->suddenDeath = CG_RegisterAnnouncerClip( folder, "sudden_death" );
	set->oneFrag = CG_RegisterAnnouncerClip( folder, "1_frag" );
	set->twoFrag = CG_RegisterAnnouncerClip( folder, "2_frags" );
	set->threeFrag = CG_RegisterAnnouncerClip( folder, "3_frags" );
}

/*
============
CG_RegisterRaceCueSound

Attempts to register a race HUD cue sound with sensible fallbacks.
============
*/
static sfxHandle_t CG_RegisterRaceCueSound( const char *name ) {
	static const char *const folders[] = { "sound/race", "sound/feedback" };
	static const char *const prefixes[] = { "", "race_" };
	static const char *const exts[] = { ".ogg", ".wav" };
	char		path[MAX_QPATH];
	sfxHandle_t	sfx;
	int		folderIndex;
	int		prefixIndex;
	int		extIndex;

	for ( folderIndex = 0; folderIndex < 2; folderIndex++ ) {
		for ( prefixIndex = 0; prefixIndex < 2; prefixIndex++ ) {
			for ( extIndex = 0; extIndex < 2; extIndex++ ) {
				Com_sprintf( path, sizeof( path ), "%s/%s%s%s", folders[folderIndex], prefixes[prefixIndex], name, exts[extIndex] );
				sfx = trap_S_RegisterSound( path, qtrue );
				if ( sfx ) {
					return sfx;
				}
			}
		}
	}

	return 0;
}

/*
============
CG_SetActiveAnnouncerProfile

Activates the media handles for the requested announcer profile.
============
*/
static void CG_SetActiveAnnouncerProfile( cgAnnouncerProfile_t profile ) {
	const cgAnnouncerSoundSet_t	*set;
	const cgAnnouncerSoundSet_t	*fallback;

	if ( profile <= ANNOUNCER_PROFILE_DISABLED || profile >= ANNOUNCER_PROFILE_COUNT ) {
		profile = ANNOUNCER_PROFILE_DISABLED;
	}

	cgs.announcerProfile = profile;

	if ( profile == ANNOUNCER_PROFILE_DISABLED ) {
		cgs.media.oneMinuteSound = 0;
		cgs.media.fiveMinuteSound = 0;
		cgs.media.suddenDeathSound = 0;
		cgs.media.oneFragSound = 0;
		cgs.media.twoFragSound = 0;
		cgs.media.threeFragSound = 0;
		return;
	}

	set = &cgs.media.announcerSoundSets[profile];
	fallback = &cgs.media.announcerSoundSets[ANNOUNCER_PROFILE_DEFAULT];

	#define CG_APPLY_ANNOUNCER_HANDLE(member) \
		cgs.media.member = set->member ? set->member : fallback->member

	CG_APPLY_ANNOUNCER_HANDLE( oneMinuteSound );
	CG_APPLY_ANNOUNCER_HANDLE( fiveMinuteSound );
	CG_APPLY_ANNOUNCER_HANDLE( suddenDeathSound );
	CG_APPLY_ANNOUNCER_HANDLE( oneFragSound );
	CG_APPLY_ANNOUNCER_HANDLE( twoFragSound );
	CG_APPLY_ANNOUNCER_HANDLE( threeFragSound );

	#undef CG_APPLY_ANNOUNCER_HANDLE
}

/*
============
CG_UpdateAnnouncerProfileFromCvar

Synchronizes the active announcer set with the cg_announcer cvar.
============
*/
static void CG_UpdateAnnouncerProfileFromCvar( qboolean force ) {
	cgAnnouncerProfile_t	profile;

	switch ( cg_announcer.integer ) {
		case 0:
			profile = ANNOUNCER_PROFILE_DISABLED;
			break;
		case 2:
			profile = ANNOUNCER_PROFILE_VADRIGAR;
			break;
		case 3:
			profile = ANNOUNCER_PROFILE_DAEMIA;
			break;
		default:
			profile = ANNOUNCER_PROFILE_DEFAULT;
			break;
	}

	if ( !force && profile == cgs.announcerProfile ) {
		return;
	}

	CG_SetActiveAnnouncerProfile( profile );
}

/*
=================
CG_RegisterSounds

called during a precache command
=================
*/
static void CG_RegisterSounds( void ) {
	int		i;
	char	items[MAX_ITEMS+1];
	char	name[MAX_QPATH];
	const char	*soundName;

	// voice commands
	CG_LoadVoiceChats();

	CG_RegisterAnnouncerVoiceSet( ANNOUNCER_PROFILE_DEFAULT, NULL );
	CG_RegisterAnnouncerVoiceSet( ANNOUNCER_PROFILE_VADRIGAR, "vadrigar" );
	CG_RegisterAnnouncerVoiceSet( ANNOUNCER_PROFILE_DAEMIA, "daemia" );
	CG_UpdateAnnouncerProfileFromCvar( qtrue );
	cgs.media.count3Sound = trap_S_RegisterSound( "sound/feedback/three.wav", qtrue );
	cgs.media.count2Sound = trap_S_RegisterSound( "sound/feedback/two.wav", qtrue );
	cgs.media.count1Sound = trap_S_RegisterSound( "sound/feedback/one.wav", qtrue );
	cgs.media.countFightSound = trap_S_RegisterSound( "sound/feedback/fight.wav", qtrue );
	cgs.media.countPrepareSound = trap_S_RegisterSound( "sound/feedback/prepare.wav", qtrue );
	cgs.media.countPrepareTeamSound = trap_S_RegisterSound( "sound/feedback/prepare_team.wav", qtrue );
	cgs.media.raceStartBeep = CG_RegisterRaceCueSound( "start" );
	cgs.media.raceCheckpointBeep = CG_RegisterRaceCueSound( "checkpoint" );
	cgs.media.raceFinishBeep = CG_RegisterRaceCueSound( "finish" );

	if ( cgs.gametype >= GT_TEAM || cg_buildScript.integer ) {

		cgs.media.captureAwardSound = trap_S_RegisterSound( "sound/teamplay/flagcapture_yourteam.wav", qtrue );
		cgs.media.redLeadsSound = trap_S_RegisterSound( "sound/feedback/redleads.wav", qtrue );
		cgs.media.blueLeadsSound = trap_S_RegisterSound( "sound/feedback/blueleads.wav", qtrue );
		cgs.media.teamsTiedSound = trap_S_RegisterSound( "sound/feedback/teamstied.wav", qtrue );
		cgs.media.hitTeamSound = trap_S_RegisterSound( "sound/feedback/hit_teammate.wav", qtrue );

		cgs.media.redScoredSound = trap_S_RegisterSound( "sound/teamplay/voc_red_scores.wav", qtrue );
		cgs.media.blueScoredSound = trap_S_RegisterSound( "sound/teamplay/voc_blue_scores.wav", qtrue );

		cgs.media.captureYourTeamSound = trap_S_RegisterSound( "sound/teamplay/flagcapture_yourteam.wav", qtrue );
		cgs.media.captureOpponentSound = trap_S_RegisterSound( "sound/teamplay/flagcapture_opponent.wav", qtrue );

		cgs.media.returnYourTeamSound = trap_S_RegisterSound( "sound/teamplay/flagreturn_yourteam.wav", qtrue );
		cgs.media.returnOpponentSound = trap_S_RegisterSound( "sound/teamplay/flagreturn_opponent.wav", qtrue );

		cgs.media.takenYourTeamSound = trap_S_RegisterSound( "sound/teamplay/flagtaken_yourteam.wav", qtrue );
		cgs.media.takenOpponentSound = trap_S_RegisterSound( "sound/teamplay/flagtaken_opponent.wav", qtrue );

		if ( cgs.gametype == GT_CTF || cg_buildScript.integer ) {
			cgs.media.redFlagReturnedSound = trap_S_RegisterSound( "sound/teamplay/voc_red_returned.wav", qtrue );
			cgs.media.blueFlagReturnedSound = trap_S_RegisterSound( "sound/teamplay/voc_blue_returned.wav", qtrue );
			cgs.media.enemyTookYourFlagSound = trap_S_RegisterSound( "sound/teamplay/voc_enemy_flag.wav", qtrue );
			cgs.media.yourTeamTookEnemyFlagSound = trap_S_RegisterSound( "sound/teamplay/voc_team_flag.wav", qtrue );
		}

		if ( cgs.gametype == GT_1FCTF || cg_buildScript.integer ) {
			// FIXME: get a replacement for this sound ?
			cgs.media.neutralFlagReturnedSound = trap_S_RegisterSound( "sound/teamplay/flagreturn_opponent.wav", qtrue );
			cgs.media.yourTeamTookTheFlagSound = trap_S_RegisterSound( "sound/teamplay/voc_team_1flag.wav", qtrue );
			cgs.media.enemyTookTheFlagSound = trap_S_RegisterSound( "sound/teamplay/voc_enemy_1flag.wav", qtrue );
		}

		if ( cgs.gametype == GT_1FCTF || cgs.gametype == GT_CTF || cg_buildScript.integer ) {
			cgs.media.youHaveFlagSound = trap_S_RegisterSound( "sound/teamplay/voc_you_flag.wav", qtrue );
			cgs.media.holyShitSound = trap_S_RegisterSound("sound/feedback/voc_holyshit.wav", qtrue);
		}

		if ( cgs.gametype == GT_OBELISK || cg_buildScript.integer ) {
			cgs.media.yourBaseIsUnderAttackSound = trap_S_RegisterSound( "sound/teamplay/voc_base_attack.wav", qtrue );
		}

		if ( cgs.gametype == GT_DOMINATION || cg_buildScript.integer ) {
			cgs.media.dominationDistressSound = trap_S_RegisterSound( "sound/feedback/domination_distress.wav", qtrue );
		}
	}

	cgs.media.tracerSound = trap_S_RegisterSound( "sound/weapons/machinegun/buletby1.wav", qfalse );
	cgs.media.selectSound = trap_S_RegisterSound( "sound/weapons/change.wav", qfalse );
	cgs.media.wearOffSound = trap_S_RegisterSound( "sound/items/wearoff.wav", qfalse );
	cgs.media.useNothingSound = trap_S_RegisterSound( "sound/items/use_nothing.wav", qfalse );
	cgs.media.gibSound = trap_S_RegisterSound( "sound/player/gibsplt1.wav", qfalse );
	cgs.media.gibBounce1Sound = trap_S_RegisterSound( "sound/player/gibimp1.wav", qfalse );
	cgs.media.gibBounce2Sound = trap_S_RegisterSound( "sound/player/gibimp2.wav", qfalse );
	cgs.media.gibBounce3Sound = trap_S_RegisterSound( "sound/player/gibimp3.wav", qfalse );

	cgs.media.useInvulnerabilitySound = trap_S_RegisterSound( "sound/items/invul_activate.wav", qfalse );
	cgs.media.invulnerabilityImpactSound1 = trap_S_RegisterSound( "sound/items/invul_impact_01.wav", qfalse );
	cgs.media.invulnerabilityImpactSound2 = trap_S_RegisterSound( "sound/items/invul_impact_02.wav", qfalse );
	cgs.media.invulnerabilityImpactSound3 = trap_S_RegisterSound( "sound/items/invul_impact_03.wav", qfalse );
	cgs.media.invulnerabilityJuicedSound = trap_S_RegisterSound( "sound/items/invul_juiced.wav", qfalse );
	cgs.media.obeliskHitSound1 = trap_S_RegisterSound( "sound/items/obelisk_hit_01.wav", qfalse );
	cgs.media.obeliskHitSound2 = trap_S_RegisterSound( "sound/items/obelisk_hit_02.wav", qfalse );
	cgs.media.obeliskHitSound3 = trap_S_RegisterSound( "sound/items/obelisk_hit_03.wav", qfalse );
	cgs.media.obeliskRespawnSound = trap_S_RegisterSound( "sound/items/obelisk_respawn.wav", qfalse );

	cgs.media.ammoregenSound = trap_S_RegisterSound("sound/items/cl_ammoregen.wav", qfalse);
	cgs.media.doublerSound = trap_S_RegisterSound("sound/items/cl_doubler.wav", qfalse);
	cgs.media.guardSound = trap_S_RegisterSound("sound/items/cl_guard.wav", qfalse);
	cgs.media.scoutSound = trap_S_RegisterSound("sound/items/cl_scout.wav", qfalse);

	cgs.media.teleInSound = trap_S_RegisterSound( "sound/world/telein.wav", qfalse );
	cgs.media.teleOutSound = trap_S_RegisterSound( "sound/world/teleout.wav", qfalse );
	cgs.media.respawnSound = trap_S_RegisterSound( "sound/items/respawn1.wav", qfalse );

	cgs.media.noAmmoSound = trap_S_RegisterSound( "sound/weapons/noammo.wav", qfalse );

	cgs.media.talkSound = trap_S_RegisterSound( "sound/player/talk.wav", qfalse );
	cgs.media.landSound = trap_S_RegisterSound( "sound/player/land1.wav", qfalse);

	cgs.media.hitSound = trap_S_RegisterSound( "sound/feedback/hit.wav", qfalse );
	cgs.media.hitSoundHighArmor = trap_S_RegisterSound( "sound/feedback/hithi.wav", qfalse );
	cgs.media.hitSoundLowArmor = trap_S_RegisterSound( "sound/feedback/hitlo.wav", qfalse );

	cgs.media.impressiveSound = trap_S_RegisterSound( "sound/feedback/impressive.wav", qtrue );
	cgs.media.excellentSound = trap_S_RegisterSound( "sound/feedback/excellent.wav", qtrue );
	cgs.media.deniedSound = trap_S_RegisterSound( "sound/feedback/denied.wav", qtrue );
	cgs.media.humiliationSound = trap_S_RegisterSound( "sound/feedback/humiliation.wav", qtrue );
	cgs.media.assistSound = trap_S_RegisterSound( "sound/feedback/assist.wav", qtrue );
	cgs.media.defendSound = trap_S_RegisterSound( "sound/feedback/defense.wav", qtrue );
	cgs.media.firstImpressiveSound = trap_S_RegisterSound( "sound/feedback/first_impressive.wav", qtrue );
	cgs.media.firstExcellentSound = trap_S_RegisterSound( "sound/feedback/first_excellent.wav", qtrue );
	cgs.media.firstHumiliationSound = trap_S_RegisterSound( "sound/feedback/first_gauntlet.wav", qtrue );

	cgs.media.takenLeadSound = trap_S_RegisterSound( "sound/feedback/takenlead.wav", qtrue);
	cgs.media.tiedLeadSound = trap_S_RegisterSound( "sound/feedback/tiedlead.wav", qtrue);
	cgs.media.lostLeadSound = trap_S_RegisterSound( "sound/feedback/lostlead.wav", qtrue);

	cgs.media.voteNow = trap_S_RegisterSound( "sound/feedback/vote_now.wav", qtrue);
	cgs.media.votePassed = trap_S_RegisterSound( "sound/feedback/vote_passed.wav", qtrue);
	cgs.media.voteFailed = trap_S_RegisterSound( "sound/feedback/vote_failed.wav", qtrue);

	cgs.media.watrInSound = trap_S_RegisterSound( "sound/player/watr_in.wav", qfalse);
	cgs.media.watrOutSound = trap_S_RegisterSound( "sound/player/watr_out.wav", qfalse);
	cgs.media.watrUnSound = trap_S_RegisterSound( "sound/player/watr_un.wav", qfalse);

	cgs.media.jumpPadSound = trap_S_RegisterSound ("sound/world/jumppad.wav", qfalse );

	for (i=0 ; i<4 ; i++) {
		Com_sprintf (name, sizeof(name), "sound/player/footsteps/step%i.wav", i+1);
		cgs.media.footsteps[FOOTSTEP_NORMAL][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/boot%i.wav", i+1);
		cgs.media.footsteps[FOOTSTEP_BOOT][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/flesh%i.wav", i+1);
		cgs.media.footsteps[FOOTSTEP_FLESH][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/mech%i.wav", i+1);
		cgs.media.footsteps[FOOTSTEP_MECH][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/energy%i.wav", i+1);
		cgs.media.footsteps[FOOTSTEP_ENERGY][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/splash%i.wav", i+1);
		cgs.media.footsteps[FOOTSTEP_SPLASH][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/clank%i.wav", i+1);
		cgs.media.footsteps[FOOTSTEP_METAL][i] = trap_S_RegisterSound (name, qfalse);
	}

	// only register the items that the server says we need
	strcpy( items, CG_ConfigString( CS_ITEMS ) );

	for ( i = 1 ; i < bg_numItems ; i++ ) {
//		if ( items[ i ] == '1' || cg_buildScript.integer ) {
			CG_RegisterItemSounds( i );
//		}
	}

	for ( i = 1 ; i < MAX_SOUNDS ; i++ ) {
		soundName = CG_ConfigString( CS_SOUNDS+i );
		if ( !soundName[0] ) {
			break;
		}
		if ( soundName[0] == '*' ) {
			continue;	// custom sound
		}
		cgs.gameSounds[i] = trap_S_RegisterSound( soundName, qfalse );
	}

	// FIXME: only needed with item
	cgs.media.flightSound = trap_S_RegisterSound( "sound/items/flight.wav", qfalse );
	cgs.media.medkitSound = trap_S_RegisterSound ("sound/items/use_medkit.wav", qfalse);
	cgs.media.quadSound = trap_S_RegisterSound("sound/items/damage3.wav", qfalse);
	cgs.media.sfx_ric1 = trap_S_RegisterSound ("sound/weapons/machinegun/ric1.wav", qfalse);
	cgs.media.sfx_ric2 = trap_S_RegisterSound ("sound/weapons/machinegun/ric2.wav", qfalse);
	cgs.media.sfx_ric3 = trap_S_RegisterSound ("sound/weapons/machinegun/ric3.wav", qfalse);
	cgs.media.sfx_railg = trap_S_RegisterSound ("sound/weapons/railgun/railgf1a.wav", qfalse);
	cgs.media.sfx_rockexp = trap_S_RegisterSound ("sound/weapons/rocket/rocklx1a.wav", qfalse);
	cgs.media.sfx_plasmaexp = trap_S_RegisterSound ("sound/weapons/plasma/plasmx1a.wav", qfalse);
	cgs.media.sfx_proxexp = trap_S_RegisterSound( "sound/weapons/proxmine/wstbexpl.wav" , qfalse);
	cgs.media.sfx_nghit = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpd.wav" , qfalse);
	cgs.media.sfx_nghitflesh = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpl.wav" , qfalse);
	cgs.media.sfx_nghitmetal = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpm.wav", qfalse );
	cgs.media.sfx_chghit = trap_S_RegisterSound( "sound/weapons/vulcan/wvulimpd.wav", qfalse );
	cgs.media.sfx_chghitflesh = trap_S_RegisterSound( "sound/weapons/vulcan/wvulimpl.wav", qfalse );
	cgs.media.sfx_chghitmetal = trap_S_RegisterSound( "sound/weapons/vulcan/wvulimpm.wav", qfalse );
	cgs.media.weaponHoverSound = trap_S_RegisterSound( "sound/weapons/weapon_hover.wav", qfalse );
	cgs.media.kamikazeExplodeSound = trap_S_RegisterSound( "sound/items/kam_explode.wav", qfalse );
	cgs.media.kamikazeImplodeSound = trap_S_RegisterSound( "sound/items/kam_implode.wav", qfalse );
	cgs.media.kamikazeFarSound = trap_S_RegisterSound( "sound/items/kam_explode_far.wav", qfalse );
	cgs.media.winnerSound = trap_S_RegisterSound( "sound/feedback/voc_youwin.wav", qfalse );
	cgs.media.loserSound = trap_S_RegisterSound( "sound/feedback/voc_youlose.wav", qfalse );
	cgs.media.youSuckSound = trap_S_RegisterSound( "sound/misc/yousuck.wav", qfalse );

	cgs.media.wstbimplSound = trap_S_RegisterSound("sound/weapons/proxmine/wstbimpl.wav", qfalse);
	cgs.media.wstbimpmSound = trap_S_RegisterSound("sound/weapons/proxmine/wstbimpm.wav", qfalse);
	cgs.media.wstbimpdSound = trap_S_RegisterSound("sound/weapons/proxmine/wstbimpd.wav", qfalse);
	cgs.media.wstbactvSound = trap_S_RegisterSound("sound/weapons/proxmine/wstbactv.wav", qfalse);

	cgs.media.regenSound = trap_S_RegisterSound("sound/items/regen.wav", qfalse);
	cgs.media.protectSound = trap_S_RegisterSound("sound/items/protect3.wav", qfalse);
	cgs.media.n_healthSound = trap_S_RegisterSound("sound/items/n_health.wav", qfalse );
	cgs.media.hgrenb1aSound = trap_S_RegisterSound("sound/weapons/grenade/hgrenb1a.wav", qfalse);
	cgs.media.hgrenb2aSound = trap_S_RegisterSound("sound/weapons/grenade/hgrenb2a.wav", qfalse);

	trap_S_RegisterSound("sound/player/james/death1.wav", qfalse );
	trap_S_RegisterSound("sound/player/james/death2.wav", qfalse );
	trap_S_RegisterSound("sound/player/james/death3.wav", qfalse );
	trap_S_RegisterSound("sound/player/james/jump1.wav", qfalse );
	trap_S_RegisterSound("sound/player/james/pain25_1.wav", qfalse );
	trap_S_RegisterSound("sound/player/james/pain75_1.wav", qfalse );
	trap_S_RegisterSound("sound/player/james/pain100_1.wav", qfalse );
	trap_S_RegisterSound("sound/player/james/falling1.wav", qfalse );
	trap_S_RegisterSound("sound/player/james/gasp.wav", qfalse );
	trap_S_RegisterSound("sound/player/james/drown.wav", qfalse );
	trap_S_RegisterSound("sound/player/james/fall1.wav", qfalse );
	trap_S_RegisterSound("sound/player/james/taunt.wav", qfalse );

	trap_S_RegisterSound("sound/player/janet/death1.wav", qfalse );
	trap_S_RegisterSound("sound/player/janet/death2.wav", qfalse );
	trap_S_RegisterSound("sound/player/janet/death3.wav", qfalse );
	trap_S_RegisterSound("sound/player/janet/jump1.wav", qfalse );
	trap_S_RegisterSound("sound/player/janet/pain25_1.wav", qfalse );
	trap_S_RegisterSound("sound/player/janet/pain75_1.wav", qfalse );
	trap_S_RegisterSound("sound/player/janet/pain100_1.wav", qfalse );
	trap_S_RegisterSound("sound/player/janet/falling1.wav", qfalse );
	trap_S_RegisterSound("sound/player/janet/gasp.wav", qfalse );
	trap_S_RegisterSound("sound/player/janet/drown.wav", qfalse );
	trap_S_RegisterSound("sound/player/janet/fall1.wav", qfalse );
	trap_S_RegisterSound("sound/player/janet/taunt.wav", qfalse );

}


//===================================================================================


/*
=================
CG_RegisterGraphics

This function may execute for a couple of minutes with a slow disk.
=================
*/
static void CG_RegisterGraphics( void ) {
	int			i;
	char		items[MAX_ITEMS+1];
	static char		*sb_nums[11] = {
		"gfx/2d/numbers/zero_32b",
		"gfx/2d/numbers/one_32b",
		"gfx/2d/numbers/two_32b",
		"gfx/2d/numbers/three_32b",
		"gfx/2d/numbers/four_32b",
		"gfx/2d/numbers/five_32b",
		"gfx/2d/numbers/six_32b",
		"gfx/2d/numbers/seven_32b",
		"gfx/2d/numbers/eight_32b",
		"gfx/2d/numbers/nine_32b",
		"gfx/2d/numbers/minus_32b",
	};

	// clear any references to old media
	memset( &cg.refdef, 0, sizeof( cg.refdef ) );
	trap_R_ClearScene();

	CG_LoadingString( cgs.mapname );

	trap_R_LoadWorldMap( cgs.mapname );

	// precache status bar pics
	CG_LoadingString( "game media" );

	for ( i=0 ; i<11 ; i++) {
		cgs.media.numberShaders[i] = trap_R_RegisterShader( sb_nums[i] );
	}

	cgs.media.botSkillShaders[0] = trap_R_RegisterShader( "menu/art/skill1.tga" );
	cgs.media.botSkillShaders[1] = trap_R_RegisterShader( "menu/art/skill2.tga" );
	cgs.media.botSkillShaders[2] = trap_R_RegisterShader( "menu/art/skill3.tga" );
	cgs.media.botSkillShaders[3] = trap_R_RegisterShader( "menu/art/skill4.tga" );
	cgs.media.botSkillShaders[4] = trap_R_RegisterShader( "menu/art/skill5.tga" );

	cgs.media.viewBloodShader = trap_R_RegisterShader( "viewBloodBlend" );

	cgs.media.deferShader = trap_R_RegisterShaderNoMip( "gfx/2d/defer.tga" );

	cgs.media.scoreboardName = trap_R_RegisterShaderNoMip( "menu/tab/name.tga" );
	cgs.media.scoreboardPing = trap_R_RegisterShaderNoMip( "menu/tab/ping.tga" );
	cgs.media.scoreboardScore = trap_R_RegisterShaderNoMip( "menu/tab/score.tga" );
	cgs.media.scoreboardTime = trap_R_RegisterShaderNoMip( "menu/tab/time.tga" );
	cgs.media.scoreboxSpecShader = trap_R_RegisterShaderNoMip( "ui/assets/score/scorebox_spec.tga" );
	cgs.media.scoreboxFollowShader = trap_R_RegisterShaderNoMip( "ui/assets/score/scorebox_follow.tga" );
	cgs.media.inkFadeLeftShader = trap_R_RegisterShaderNoMip( "ui/assets/score/ink_fade_left.tga" );
	cgs.media.inkFadeRightShader = trap_R_RegisterShaderNoMip( "ui/assets/score/ink_fade_right.tga" );

	cgs.media.smokePuffShader = trap_R_RegisterShader( "smokePuff" );
	cgs.media.smokePuffRageProShader = trap_R_RegisterShader( "smokePuffRagePro" );
	cgs.media.shotgunSmokePuffShader = trap_R_RegisterShader( "shotgunSmokePuff" );
	cgs.media.nailPuffShader = trap_R_RegisterShader( "nailtrail" );
	cgs.media.blueProxMine = trap_R_RegisterModel( "models/weaphits/proxmineb.md3" );
	cgs.media.plasmaBallShader = trap_R_RegisterShader( "sprites/plasma1" );
	cgs.media.bloodTrailShader = trap_R_RegisterShader( "bloodTrail" );
	cgs.media.lagometerShader = trap_R_RegisterShader("lagometer" );
	cgs.media.connectionShader = trap_R_RegisterShader( "disconnected" );

	cgs.media.waterBubbleShader = trap_R_RegisterShader( "waterBubble" );

	cgs.media.tracerShader = trap_R_RegisterShader( "gfx/misc/tracer" );
	cgs.media.selectShader = trap_R_RegisterShader( "gfx/2d/select" );

	for ( i = 0 ; i < NUM_CROSSHAIRS ; i++ ) {
		cgs.media.crosshairShader[i] = trap_R_RegisterShader( va("gfx/2d/crosshair%c", 'a'+i) );
	}

	cgs.media.backTileShader = trap_R_RegisterShader( "gfx/2d/backtile" );
	cgs.media.noammoShader = trap_R_RegisterShader( "icons/noammo" );
	cgs.media.healthBar200 = trap_R_RegisterShaderNoMip( "ui/assets/hud/h200.tga" );
	cgs.media.healthBar100 = trap_R_RegisterShaderNoMip( "ui/assets/hud/h100.tga" );
	cgs.media.armorBar200 = trap_R_RegisterShaderNoMip( "ui/assets/hud/a200.tga" );
	cgs.media.armorBar100 = trap_R_RegisterShaderNoMip( "ui/assets/hud/a100.tga" );
	cgs.media.healthTick200 = trap_R_RegisterShaderNoMip( "ui/assets/hud/h200line.tga" );
	cgs.media.healthTick100 = trap_R_RegisterShaderNoMip( "ui/assets/hud/h100line.tga" );
	cgs.media.armorTick200 = trap_R_RegisterShaderNoMip( "ui/assets/hud/a200line.tga" );
	cgs.media.armorTick100 = trap_R_RegisterShaderNoMip( "ui/assets/hud/a100line.tga" );

	// powerup shaders
	cgs.media.quadShader = trap_R_RegisterShader("powerups/quad" );
	cgs.media.quadWeaponShader = trap_R_RegisterShader("powerups/quadWeapon" );
	cgs.media.battleSuitShader = trap_R_RegisterShader("powerups/battleSuit" );
	cgs.media.battleWeaponShader = trap_R_RegisterShader("powerups/battleWeapon" );
	cgs.media.invisShader = trap_R_RegisterShader("powerups/invisibility" );
	cgs.media.regenShader = trap_R_RegisterShader("powerups/regen" );
	cgs.media.hastePuffShader = trap_R_RegisterShader("hasteSmokePuff" );

	if ( cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF || cgs.gametype == GT_HARVESTER || cg_buildScript.integer ) {
		cgs.media.redCubeModel = trap_R_RegisterModel( "models/powerups/orb/r_orb.md3" );
		cgs.media.blueCubeModel = trap_R_RegisterModel( "models/powerups/orb/b_orb.md3" );
		cgs.media.redCubeIcon = trap_R_RegisterShader( "icons/skull_red" );
		cgs.media.blueCubeIcon = trap_R_RegisterShader( "icons/skull_blue" );
	}

	if ( cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF || cgs.gametype == GT_HARVESTER || cg_buildScript.integer ) {
		cgs.media.redFlagModel = trap_R_RegisterModel( "models/flags/r_flag.md3" );
		cgs.media.blueFlagModel = trap_R_RegisterModel( "models/flags/b_flag.md3" );
		cgs.media.redFlagShader[0] = trap_R_RegisterShaderNoMip( "icons/iconf_red1" );
		cgs.media.redFlagShader[1] = trap_R_RegisterShaderNoMip( "icons/iconf_red2" );
		cgs.media.redFlagShader[2] = trap_R_RegisterShaderNoMip( "icons/iconf_red3" );
		cgs.media.blueFlagShader[0] = trap_R_RegisterShaderNoMip( "icons/iconf_blu1" );
		cgs.media.blueFlagShader[1] = trap_R_RegisterShaderNoMip( "icons/iconf_blu2" );
		cgs.media.blueFlagShader[2] = trap_R_RegisterShaderNoMip( "icons/iconf_blu3" );
		cgs.media.flagPoleModel = trap_R_RegisterModel( "models/flag2/flagpole.md3" );
		cgs.media.flagFlapModel = trap_R_RegisterModel( "models/flag2/flagflap3.md3" );

		cgs.media.redFlagFlapSkin = trap_R_RegisterSkin( "models/flag2/red.skin" );
		cgs.media.blueFlagFlapSkin = trap_R_RegisterSkin( "models/flag2/blue.skin" );
		cgs.media.neutralFlagFlapSkin = trap_R_RegisterSkin( "models/flag2/white.skin" );

		cgs.media.redFlagBaseModel = trap_R_RegisterModel( "models/mapobjects/flagbase/red_base.md3" );
		cgs.media.blueFlagBaseModel = trap_R_RegisterModel( "models/mapobjects/flagbase/blue_base.md3" );
		cgs.media.neutralFlagBaseModel = trap_R_RegisterModel( "models/mapobjects/flagbase/ntrl_base.md3" );
	}

	if ( cgs.gametype == GT_1FCTF || cg_buildScript.integer ) {
		cgs.media.neutralFlagModel = trap_R_RegisterModel( "models/flags/n_flag.md3" );
		cgs.media.flagShader[0] = trap_R_RegisterShaderNoMip( "icons/iconf_neutral1" );
		cgs.media.flagShader[1] = trap_R_RegisterShaderNoMip( "icons/iconf_red2" );
		cgs.media.flagShader[2] = trap_R_RegisterShaderNoMip( "icons/iconf_blu2" );
		cgs.media.flagShader[3] = trap_R_RegisterShaderNoMip( "icons/iconf_neutral3" );
	}

	if ( cgs.gametype == GT_OBELISK || cg_buildScript.integer ) {
		cgs.media.overloadBaseModel = trap_R_RegisterModel( "models/powerups/overload_base.md3" );
		cgs.media.overloadTargetModel = trap_R_RegisterModel( "models/powerups/overload_target.md3" );
		cgs.media.overloadLightsModel = trap_R_RegisterModel( "models/powerups/overload_lights.md3" );
		cgs.media.overloadEnergyModel = trap_R_RegisterModel( "models/powerups/overload_energy.md3" );
	}

	if ( cgs.gametype == GT_HARVESTER || cg_buildScript.integer ) {
		cgs.media.harvesterModel = trap_R_RegisterModel( "models/powerups/harvester/harvester.md3" );
		cgs.media.harvesterRedSkin = trap_R_RegisterSkin( "models/powerups/harvester/red.skin" );
		cgs.media.harvesterBlueSkin = trap_R_RegisterSkin( "models/powerups/harvester/blue.skin" );
		cgs.media.harvesterNeutralModel = trap_R_RegisterModel( "models/powerups/obelisk/obelisk.md3" );
	}

	if ( cgs.gametype == GT_DOMINATION || cg_buildScript.integer ) {
		static const char *const domCapNames[DOM_POINT_STATE_COUNT] = {
			"gfx/2d/dom_point/dom_cap_a",
			"gfx/2d/dom_point/dom_cap_b",
			"gfx/2d/dom_point/dom_cap_c",
			"gfx/2d/dom_point/dom_cap_d",
			"gfx/2d/dom_point/dom_cap_e"
		};
		static const char *const domCapDistressNames[DOM_POINT_STATE_COUNT] = {
			"gfx/2d/dom_point/dom_cap_a_dist",
			"gfx/2d/dom_point/dom_cap_b_dist",
			"gfx/2d/dom_point/dom_cap_c_dist",
			"gfx/2d/dom_point/dom_cap_d_dist",
			"gfx/2d/dom_point/dom_cap_e_dist"
		};
		static const char *const domDefNames[DOM_POINT_STATE_COUNT] = {
			"gfx/2d/dom_point/dom_def_a",
			"gfx/2d/dom_point/dom_def_b",
			"gfx/2d/dom_point/dom_def_c",
			"gfx/2d/dom_point/dom_def_d",
			"gfx/2d/dom_point/dom_def_e"
		};
		static const char *const domDefDistressNames[DOM_POINT_STATE_COUNT] = {
			"gfx/2d/dom_point/dom_def_a_dist",
			"gfx/2d/dom_point/dom_def_b_dist",
			"gfx/2d/dom_point/dom_def_c_dist",
			"gfx/2d/dom_point/dom_def_d_dist",
			"gfx/2d/dom_point/dom_def_e_dist"
		};

		cgs.media.domPointModel = trap_R_RegisterModel( "models/powerups/domination/dompoint.md3" );
		cgs.media.domPointSkinRed = trap_R_RegisterSkin( "models/powerups/domination/domred.skin" );
		cgs.media.domPointSkinBlue = trap_R_RegisterSkin( "models/powerups/domination/domblue.skin" );
		cgs.media.domPointSkinNeutral = trap_R_RegisterSkin( "models/powerups/domination/domntrl.skin" );

		for ( i = 0; i < DOM_POINT_STATE_COUNT; i++ ) {
			cgs.media.domCapShaders[i] = trap_R_RegisterShader( domCapNames[i] );
			cgs.media.domCapDistressShaders[i] = trap_R_RegisterShader( domCapDistressNames[i] );
			cgs.media.domDefShaders[i] = trap_R_RegisterShader( domDefNames[i] );
			cgs.media.domDefDistressShaders[i] = trap_R_RegisterShader( domDefDistressNames[i] );
		}
	}

	cgs.media.redKamikazeShader = trap_R_RegisterShader( "models/weaphits/kamikred" );
	cgs.media.dustPuffShader = trap_R_RegisterShader("hasteSmokePuff" );

	if ( cgs.gametype >= GT_TEAM || cg_buildScript.integer ) {
		cgs.media.friendShader = trap_R_RegisterShader( "sprites/foe" );
		if ( cgs.gametype == GT_FREEZE || cg_buildScript.integer ) {
			cgs.media.frozenPlayerShader = trap_R_RegisterShader( "sprites/frozen" );
		}
		cgs.media.redQuadShader = trap_R_RegisterShader("powerups/blueflag" );
		cgs.media.teamStatusBar = trap_R_RegisterShader( "gfx/2d/colorbar.tga" );
		cgs.media.blueKamikazeShader = trap_R_RegisterShader( "models/weaphits/kamikblu" );
	}

	cgs.media.armorModel = trap_R_RegisterModel( "models/powerups/armor/armor_yel.md3" );
	cgs.media.armorIcon  = trap_R_RegisterShaderNoMip( "icons/iconr_yellow" );

	cgs.media.machinegunBrassModel = trap_R_RegisterModel( "models/weapons2/shells/m_shell.md3" );
	cgs.media.shotgunBrassModel = trap_R_RegisterModel( "models/weapons2/shells/s_shell.md3" );

	cgs.media.gibAbdomen = trap_R_RegisterModel( "models/gibs/abdomen.md3" );
	cgs.media.gibArm = trap_R_RegisterModel( "models/gibs/arm.md3" );
	cgs.media.gibChest = trap_R_RegisterModel( "models/gibs/chest.md3" );
	cgs.media.gibFist = trap_R_RegisterModel( "models/gibs/fist.md3" );
	cgs.media.gibFoot = trap_R_RegisterModel( "models/gibs/foot.md3" );
	cgs.media.gibForearm = trap_R_RegisterModel( "models/gibs/forearm.md3" );
	cgs.media.gibIntestine = trap_R_RegisterModel( "models/gibs/intestine.md3" );
	cgs.media.gibLeg = trap_R_RegisterModel( "models/gibs/leg.md3" );
	cgs.media.gibSkull = trap_R_RegisterModel( "models/gibs/skull.md3" );
	cgs.media.gibBrain = trap_R_RegisterModel( "models/gibs/brain.md3" );

	cgs.media.smoke2 = trap_R_RegisterModel( "models/weapons2/shells/s_shell.md3" );

	cgs.media.balloonShader = trap_R_RegisterShader( "sprites/balloon3" );

	cgs.media.bloodExplosionShader = trap_R_RegisterShader( "bloodExplosion" );

	cgs.media.bulletFlashModel = trap_R_RegisterModel("models/weaphits/bullet.md3");
	cgs.media.ringFlashModel = trap_R_RegisterModel("models/weaphits/ring02.md3");
	cgs.media.dishFlashModel = trap_R_RegisterModel("models/weaphits/boom01.md3");
	cgs.media.teleportEffectModel = trap_R_RegisterModel( "models/powerups/pop.md3" );
	cgs.media.kamikazeEffectModel = trap_R_RegisterModel( "models/weaphits/kamboom2.md3" );
	cgs.media.kamikazeShockWave = trap_R_RegisterModel( "models/weaphits/kamwave.md3" );
	cgs.media.kamikazeHeadModel = trap_R_RegisterModel( "models/powerups/kamikazi.md3" );
	cgs.media.kamikazeHeadTrail = trap_R_RegisterModel( "models/powerups/trailtest.md3" );
	cgs.media.guardPowerupModel = trap_R_RegisterModel( "models/powerups/guard_player.md3" );
	cgs.media.scoutPowerupModel = trap_R_RegisterModel( "models/powerups/scout_player.md3" );
	cgs.media.doublerPowerupModel = trap_R_RegisterModel( "models/powerups/doubler_player.md3" );
	cgs.media.ammoRegenPowerupModel = trap_R_RegisterModel( "models/powerups/ammo_player.md3" );
	cgs.media.invulnerabilityImpactModel = trap_R_RegisterModel( "models/powerups/shield/impact.md3" );
	cgs.media.invulnerabilityJuicedModel = trap_R_RegisterModel( "models/powerups/shield/juicer.md3" );
	cgs.media.medkitUsageModel = trap_R_RegisterModel( "models/powerups/regen.md3" );
	cgs.media.heartShader = trap_R_RegisterShaderNoMip( "ui/assets/statusbar/selectedhealth.tga" );


	cgs.media.invulnerabilityPowerupModel = trap_R_RegisterModel( "models/powerups/shield/shield.md3" );
	cgs.media.medalImpressive = trap_R_RegisterShaderNoMip( "medal_impressive" );
	cgs.media.medalExcellent = trap_R_RegisterShaderNoMip( "medal_excellent" );
	cgs.media.medalGauntlet = trap_R_RegisterShaderNoMip( "medal_gauntlet" );
	cgs.media.medalDefend = trap_R_RegisterShaderNoMip( "medal_defend" );
	cgs.media.medalAssist = trap_R_RegisterShaderNoMip( "medal_assist" );
	cgs.media.medalCapture = trap_R_RegisterShaderNoMip( "medal_capture" );


	memset( cg_items, 0, sizeof( cg_items ) );
	memset( cg_weapons, 0, sizeof( cg_weapons ) );

	// only register the items that the server says we need
	strcpy( items, CG_ConfigString( CS_ITEMS) );

	for ( i = 1 ; i < bg_numItems ; i++ ) {
		if ( items[ i ] == '1' || cg_buildScript.integer ) {
			CG_LoadingItem( i );
			CG_RegisterItemVisuals( i );
		}
	}

	// wall marks
	cgs.media.bulletMarkShader = trap_R_RegisterShader( "gfx/damage/bullet_mrk" );
	cgs.media.burnMarkShader = trap_R_RegisterShader( "gfx/damage/burn_med_mrk" );
	cgs.media.holeMarkShader = trap_R_RegisterShader( "gfx/damage/hole_lg_mrk" );
	cgs.media.energyMarkShader = trap_R_RegisterShader( "gfx/damage/plasma_mrk" );
	cgs.media.shadowMarkShader = trap_R_RegisterShader( "markShadow" );
	cgs.media.wakeMarkShader = trap_R_RegisterShader( "wake" );
	cgs.media.bloodMarkShader = trap_R_RegisterShader( "bloodMark" );

	// register the inline models
	cgs.numInlineModels = trap_CM_NumInlineModels();
	for ( i = 1 ; i < cgs.numInlineModels ; i++ ) {
		char	name[10];
		vec3_t			mins, maxs;
		int				j;

		Com_sprintf( name, sizeof(name), "*%i", i );
		cgs.inlineDrawModel[i] = trap_R_RegisterModel( name );
		trap_R_ModelBounds( cgs.inlineDrawModel[i], mins, maxs );
		for ( j = 0 ; j < 3 ; j++ ) {
			cgs.inlineModelMidpoints[i][j] = mins[j] + 0.5 * ( maxs[j] - mins[j] );
		}
	}

	// register all the server specified models
	for (i=1 ; i<MAX_MODELS ; i++) {
		const char		*modelName;

		modelName = CG_ConfigString( CS_MODELS+i );
		if ( !modelName[0] ) {
			break;
		}
		cgs.gameModels[i] = trap_R_RegisterModel( modelName );
	}

	// new stuff
	cgs.media.patrolShader = trap_R_RegisterShaderNoMip("ui/assets/statusbar/patrol.tga");
	cgs.media.assaultShader = trap_R_RegisterShaderNoMip("ui/assets/statusbar/assault.tga");
	cgs.media.campShader = trap_R_RegisterShaderNoMip("ui/assets/statusbar/camp.tga");
	cgs.media.followShader = trap_R_RegisterShaderNoMip("ui/assets/statusbar/follow.tga");
	cgs.media.defendShader = trap_R_RegisterShaderNoMip("ui/assets/statusbar/defend.tga");
	cgs.media.teamLeaderShader = trap_R_RegisterShaderNoMip("ui/assets/statusbar/team_leader.tga");
	cgs.media.retrieveShader = trap_R_RegisterShaderNoMip("ui/assets/statusbar/retrieve.tga");
	cgs.media.escortShader = trap_R_RegisterShaderNoMip("ui/assets/statusbar/escort.tga");
	cgs.media.cursor = trap_R_RegisterShaderNoMip( "menu/art/3_cursor2" );
	cgs.media.sizeCursor = trap_R_RegisterShaderNoMip( "ui/assets/sizecursor.tga" );
	cgs.media.selectCursor = trap_R_RegisterShaderNoMip( "ui/assets/selectcursor.tga" );
	cgs.media.flagShaders[0] = trap_R_RegisterShaderNoMip("ui/assets/statusbar/flag_in_base.tga");
	cgs.media.flagShaders[1] = trap_R_RegisterShaderNoMip("ui/assets/statusbar/flag_capture.tga");
	cgs.media.flagShaders[2] = trap_R_RegisterShaderNoMip("ui/assets/statusbar/flag_missing.tga");
	cgs.media.raceStartShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/start" );
	cgs.media.raceCheckpointShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/checkpoint" );
	cgs.media.raceFinishShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/finish" );

	trap_R_RegisterModel( "models/players/james/lower.md3" );
	trap_R_RegisterModel( "models/players/james/upper.md3" );
	trap_R_RegisterModel( "models/players/heads/james/james.md3" );

	trap_R_RegisterModel( "models/players/janet/lower.md3" );
	trap_R_RegisterModel( "models/players/janet/upper.md3" );
	trap_R_RegisterModel( "models/players/heads/janet/janet.md3" );

	CG_ClearParticles ();
/*
	for (i=1; i<MAX_PARTICLES_AREAS; i++)
	{
		{
			int rval;

			rval = CG_NewParticleArea ( CS_PARTICLES + i);
			if (!rval)
				break;
		}
	}
*/
}



/*																																			
=======================
CG_BuildSpectatorString

=======================
*/
void CG_BuildSpectatorString() {
	int i;
	cg.spectatorList[0] = 0;
	for (i = 0; i < MAX_CLIENTS; i++) {
		if (cgs.clientinfo[i].infoValid && cgs.clientinfo[i].team == TEAM_SPECTATOR ) {
			Q_strcat(cg.spectatorList, sizeof(cg.spectatorList), va("%s     ", cgs.clientinfo[i].name));
		}
	}
	i = strlen(cg.spectatorList);
	if (i != cg.spectatorLen) {
		cg.spectatorLen = i;
		cg.spectatorWidth = -1;
	}
}


/*																																			
===================
CG_RegisterClients
===================
*/
static void CG_RegisterClients( void ) {
	int		i;

	CG_LoadingClient(cg.clientNum);
	CG_NewClientInfo(cg.clientNum);

	for (i=0 ; i<MAX_CLIENTS ; i++) {
		const char		*clientInfo;

		if (cg.clientNum == i) {
			continue;
		}

		clientInfo = CG_ConfigString( CS_PLAYERS+i );
		if ( !clientInfo[0]) {
			continue;
		}
		CG_LoadingClient( i );
		CG_NewClientInfo( i );
	}
	CG_BuildSpectatorString();
}

//===========================================================================

/*
=================
CG_ConfigString
=================
*/
const char *CG_ConfigString( int index ) {
	if ( index < 0 || index >= MAX_CONFIGSTRINGS ) {
		CG_Error( "CG_ConfigString: bad index: %i", index );
	}
	return cgs.gameState.stringData + cgs.gameState.stringOffsets[ index ];
}

//==================================================================

/*
======================
CG_StartMusic

======================
*/
void CG_StartMusic( void ) {
	char	*s;
	char	parm1[MAX_QPATH], parm2[MAX_QPATH];

	// start the background music
	s = (char *)CG_ConfigString( CS_MUSIC );
	Q_strncpyz( parm1, COM_Parse( &s ), sizeof( parm1 ) );
	Q_strncpyz( parm2, COM_Parse( &s ), sizeof( parm2 ) );

	trap_S_StartBackgroundTrack( parm1, parm2 );
}
char *CG_GetMenuBuffer(const char *filename) {
	int	len;
	fileHandle_t	f;
	static char buf[MAX_MENUFILE];

	len = trap_FS_FOpenFile( filename, &f, FS_READ );
	if ( !f ) {
		trap_Print( va( S_COLOR_RED "menu file not found: %s, using default\n", filename ) );
		return NULL;
	}
	if ( len >= MAX_MENUFILE ) {
		trap_Print( va( S_COLOR_RED "menu file too large: %s is %i, max allowed is %i", filename, len, MAX_MENUFILE ) );
		trap_FS_FCloseFile( f );
		return NULL;
	}

	trap_FS_Read( buf, len, f );
	buf[len] = 0;
	trap_FS_FCloseFile( f );

	return buf;
}

//
// ==============================
// new hud stuff ( mission pack )
// ==============================
//
qboolean CG_Asset_Parse(int handle) {
	pc_token_t token;
	const char *tempStr;

	if (!trap_PC_ReadToken(handle, &token))
		return qfalse;
	if (Q_stricmp(token.string, "{") != 0) {
		return qfalse;
	}
    
	while ( 1 ) {
		if (!trap_PC_ReadToken(handle, &token))
			return qfalse;

		if (Q_stricmp(token.string, "}") == 0) {
			return qtrue;
		}

		// font
		if (Q_stricmp(token.string, "font") == 0) {
			int pointSize;
			if (!PC_String_Parse(handle, &tempStr) || !PC_Int_Parse(handle, &pointSize)) {
				return qfalse;
			}
			cgDC.registerFont(tempStr, pointSize, &cgDC.Assets.textFont);
			continue;
		}

		// smallFont
		if (Q_stricmp(token.string, "smallFont") == 0) {
			int pointSize;
			if (!PC_String_Parse(handle, &tempStr) || !PC_Int_Parse(handle, &pointSize)) {
				return qfalse;
			}
			cgDC.registerFont(tempStr, pointSize, &cgDC.Assets.smallFont);
			continue;
		}

		// font
		if (Q_stricmp(token.string, "bigfont") == 0) {
			int pointSize;
			if (!PC_String_Parse(handle, &tempStr) || !PC_Int_Parse(handle, &pointSize)) {
				return qfalse;
			}
			cgDC.registerFont(tempStr, pointSize, &cgDC.Assets.bigFont);
			continue;
		}

		// gradientbar
		if (Q_stricmp(token.string, "gradientbar") == 0) {
			if (!PC_String_Parse(handle, &tempStr)) {
				return qfalse;
			}
			cgDC.Assets.gradientBar = trap_R_RegisterShaderNoMip(tempStr);
			continue;
		}

		// enterMenuSound
		if (Q_stricmp(token.string, "menuEnterSound") == 0) {
			if (!PC_String_Parse(handle, &tempStr)) {
				return qfalse;
			}
			cgDC.Assets.menuEnterSound = trap_S_RegisterSound( tempStr, qfalse );
			continue;
		}

		// exitMenuSound
		if (Q_stricmp(token.string, "menuExitSound") == 0) {
			if (!PC_String_Parse(handle, &tempStr)) {
				return qfalse;
			}
			cgDC.Assets.menuExitSound = trap_S_RegisterSound( tempStr, qfalse );
			continue;
		}

		// itemFocusSound
		if (Q_stricmp(token.string, "itemFocusSound") == 0) {
			if (!PC_String_Parse(handle, &tempStr)) {
				return qfalse;
			}
			cgDC.Assets.itemFocusSound = trap_S_RegisterSound( tempStr, qfalse );
			continue;
		}

		// menuBuzzSound
		if (Q_stricmp(token.string, "menuBuzzSound") == 0) {
			if (!PC_String_Parse(handle, &tempStr)) {
				return qfalse;
			}
			cgDC.Assets.menuBuzzSound = trap_S_RegisterSound( tempStr, qfalse );
			continue;
		}

		if (Q_stricmp(token.string, "cursor") == 0) {
			if (!PC_String_Parse(handle, &cgDC.Assets.cursorStr)) {
				return qfalse;
			}
			cgDC.Assets.cursor = trap_R_RegisterShaderNoMip( cgDC.Assets.cursorStr);
			continue;
		}

		if (Q_stricmp(token.string, "fadeClamp") == 0) {
			if (!PC_Float_Parse(handle, &cgDC.Assets.fadeClamp)) {
				return qfalse;
			}
			continue;
		}

		if (Q_stricmp(token.string, "fadeCycle") == 0) {
			if (!PC_Int_Parse(handle, &cgDC.Assets.fadeCycle)) {
				return qfalse;
			}
			continue;
		}

		if (Q_stricmp(token.string, "fadeAmount") == 0) {
			if (!PC_Float_Parse(handle, &cgDC.Assets.fadeAmount)) {
				return qfalse;
			}
			continue;
		}

		if (Q_stricmp(token.string, "shadowX") == 0) {
			if (!PC_Float_Parse(handle, &cgDC.Assets.shadowX)) {
				return qfalse;
			}
			continue;
		}

		if (Q_stricmp(token.string, "shadowY") == 0) {
			if (!PC_Float_Parse(handle, &cgDC.Assets.shadowY)) {
				return qfalse;
			}
			continue;
		}

		if (Q_stricmp(token.string, "shadowColor") == 0) {
			if (!PC_Color_Parse(handle, &cgDC.Assets.shadowColor)) {
				return qfalse;
			}
			cgDC.Assets.shadowFadeClamp = cgDC.Assets.shadowColor[3];
			continue;
		}
	}
	return qfalse; // bk001204 - why not?
}

void CG_ParseMenu(const char *menuFile) {
	pc_token_t token;
	int handle;

	handle = trap_PC_LoadSource(menuFile);
	if (!handle)
		handle = trap_PC_LoadSource("ui/testhud.menu");
	if (!handle)
		return;

	while ( 1 ) {
		if (!trap_PC_ReadToken( handle, &token )) {
			break;
		}

		//if ( Q_stricmp( token, "{" ) ) {
		//	Com_Printf( "Missing { in menu file\n" );
		//	break;
		//}

		//if ( menuCount == MAX_MENUS ) {
		//	Com_Printf( "Too many menus!\n" );
		//	break;
		//}

		if ( token.string[0] == '}' ) {
			break;
		}

		if (Q_stricmp(token.string, "assetGlobalDef") == 0) {
			if (CG_Asset_Parse(handle)) {
				continue;
			} else {
				break;
			}
		}


		if (Q_stricmp(token.string, "menudef") == 0) {
			// start a new menu
			Menu_New(handle);
		}
	}
	trap_PC_FreeSource(handle);
}

qboolean CG_Load_Menu(char **p) {
	char *token;

	token = COM_ParseExt(p, qtrue);

	if (token[0] != '{') {
		return qfalse;
	}

	while ( 1 ) {

		token = COM_ParseExt(p, qtrue);
    
		if (Q_stricmp(token, "}") == 0) {
			return qtrue;
		}

		if ( !token || token[0] == 0 ) {
			return qfalse;
		}

		CG_ParseMenu(token); 
	}
	return qfalse;
}



void CG_LoadMenus(const char *menuFile) {
	char	*token;
	char *p;
	int	len, start;
	fileHandle_t	f;
	static char buf[MAX_MENUDEFFILE];

	start = trap_Milliseconds();

        len = trap_FS_FOpenFile( menuFile, &f, FS_READ );
        if ( !f ) {
                trap_Error( va( S_COLOR_YELLOW "menu file not found: %s, using default\n", menuFile ) );
                len = trap_FS_FOpenFile( CG_LEGACY_HUD_FILE, &f, FS_READ );
                if (!f) {
                        trap_Error( va( S_COLOR_RED "default menu file not found: %s, unable to continue!\n", CG_LEGACY_HUD_FILE ) );
                }
        }

	if ( len >= MAX_MENUDEFFILE ) {
		trap_Error( va( S_COLOR_RED "menu file too large: %s is %i, max allowed is %i", menuFile, len, MAX_MENUDEFFILE ) );
		trap_FS_FCloseFile( f );
		return;
	}

	trap_FS_Read( buf, len, f );
	buf[len] = 0;
	trap_FS_FCloseFile( f );

	COM_Compress(buf);

	Menu_Reset();

	p = buf;

	while ( 1 ) {
		token = COM_ParseExt( &p, qtrue );
		if( !token || token[0] == 0 || token[0] == '}') {
			break;
		}

		//if ( Q_stricmp( token, "{" ) ) {
		//	Com_Printf( "Missing { in menu file\n" );
		//	break;
		//}

		//if ( menuCount == MAX_MENUS ) {
		//	Com_Printf( "Too many menus!\n" );
		//	break;
		//}

		if ( Q_stricmp( token, "}" ) == 0 ) {
			break;
		}

		if (Q_stricmp(token, "loadmenu") == 0) {
			if (CG_Load_Menu(&p)) {
				continue;
			} else {
				break;
			}
		}
	}

	Com_Printf("UI menu load time = %d milli seconds\n", trap_Milliseconds() - start);

}



static qboolean CG_OwnerDrawHandleKey(int ownerDraw, int flags, float *special, int key) {
	return qfalse;
}


static int CG_FeederCount(float feederID) {
	int i, count;
	count = 0;
	if (feederID == FEEDER_REDTEAM_LIST) {
		for (i = 0; i < cg.numScores; i++) {
			if (cg.scores[i].team == TEAM_RED) {
				count++;
			}
		}
	} else if (feederID == FEEDER_BLUETEAM_LIST) {
		for (i = 0; i < cg.numScores; i++) {
			if (cg.scores[i].team == TEAM_BLUE) {
				count++;
			}
		}
	} else if (feederID == FEEDER_SCOREBOARD) {
		return cg.numScores;
	}
	return count;
}


void CG_SetScoreSelection(void *p) {
	menuDef_t *menu = (menuDef_t*)p;
	playerState_t *ps = &cg.snap->ps;
	int i, red, blue;
	red = blue = 0;
	for (i = 0; i < cg.numScores; i++) {
		if (cg.scores[i].team == TEAM_RED) {
			red++;
		} else if (cg.scores[i].team == TEAM_BLUE) {
			blue++;
		}
		if (ps->clientNum == cg.scores[i].client) {
			cg.selectedScore = i;
		}
	}

	if (menu == NULL) {
		// just interested in setting the selected score
		return;
	}

	if ( cgs.gametype >= GT_TEAM ) {
		int feeder = FEEDER_REDTEAM_LIST;
		i = red;
		if (cg.scores[cg.selectedScore].team == TEAM_BLUE) {
			feeder = FEEDER_BLUETEAM_LIST;
			i = blue;
		}
		Menu_SetFeederSelection(menu, feeder, i, NULL);
	} else {
		Menu_SetFeederSelection(menu, FEEDER_SCOREBOARD, cg.selectedScore, NULL);
	}
}

// FIXME: might need to cache this info
static clientInfo_t * CG_InfoFromScoreIndex(int index, int team, int *scoreIndex) {
	int i, count;
	if ( cgs.gametype >= GT_TEAM ) {
		count = 0;
		for (i = 0; i < cg.numScores; i++) {
			if (cg.scores[i].team == team) {
				if (count == index) {
					*scoreIndex = i;
					return &cgs.clientinfo[cg.scores[i].client];
				}
				count++;
			}
		}
	}
	*scoreIndex = index;
	return &cgs.clientinfo[ cg.scores[index].client ];
}

static const char *CG_FeederItemText(float feederID, int index, int column, qhandle_t *handle) {
	gitem_t *item;
	int scoreIndex = 0;
	clientInfo_t *info = NULL;
	int team = -1;
	score_t *sp = NULL;

	*handle = -1;

	if (feederID == FEEDER_REDTEAM_LIST) {
		team = TEAM_RED;
	} else if (feederID == FEEDER_BLUETEAM_LIST) {
		team = TEAM_BLUE;
	}

	info = CG_InfoFromScoreIndex(index, team, &scoreIndex);
	sp = &cg.scores[scoreIndex];

	if (info && info->infoValid) {
		switch (column) {
			case 0:
				if ( info->powerups & ( 1 << PW_NEUTRALFLAG ) ) {
					item = BG_FindItemForPowerup( PW_NEUTRALFLAG );
					*handle = cg_items[ ITEM_INDEX(item) ].icon;
				} else if ( info->powerups & ( 1 << PW_REDFLAG ) ) {
					item = BG_FindItemForPowerup( PW_REDFLAG );
					*handle = cg_items[ ITEM_INDEX(item) ].icon;
				} else if ( info->powerups & ( 1 << PW_BLUEFLAG ) ) {
					item = BG_FindItemForPowerup( PW_BLUEFLAG );
					*handle = cg_items[ ITEM_INDEX(item) ].icon;
				} else {
					if ( info->botSkill > 0 && info->botSkill <= 5 ) {
						*handle = cgs.media.botSkillShaders[ info->botSkill - 1 ];
					} else if ( info->handicap < 100 ) {
					return va("%i", info->handicap );
					}
				}
			break;
			case 1:
				if (team == -1) {
					return "";
				} else {
					*handle = CG_StatusHandle(info->teamTask);
				}
		  break;
			case 2:
				if ( cg.snap->ps.stats[ STAT_CLIENTS_READY ] & ( 1 << sp->client ) ) {
					return "Ready";
				}
				if (team == -1) {
					if (cgs.gametype == GT_TOURNAMENT) {
						return va("%i/%i", info->wins, info->losses);
					} else if (info->infoValid && info->team == TEAM_SPECTATOR ) {
						return "Spectator";
					} else {
						return "";
					}
				} else {
					if (info->teamLeader) {
						return "Leader";
					}
				}
			break;
			case 3:
				return info->name;
			break;
			case 4:
				return va("%i", info->score);
			break;
			case 5:
				return va("%4i", sp->time);
			break;
			case 6:
				if ( sp->ping == -1 ) {
					return "connecting";
				} 
				return va("%4i", sp->ping);
			break;
		}
	}

	return "";
}

static qhandle_t CG_FeederItemImage(float feederID, int index) {
	return 0;
}

static void CG_FeederSelection(float feederID, int index) {
	if ( cgs.gametype >= GT_TEAM ) {
		int i, count;
		int team = (feederID == FEEDER_REDTEAM_LIST) ? TEAM_RED : TEAM_BLUE;
		count = 0;
		for (i = 0; i < cg.numScores; i++) {
			if (cg.scores[i].team == team) {
				if (index == count) {
					cg.selectedScore = i;
				}
				count++;
			}
		}
	} else {
		cg.selectedScore = index;
	}
}

static float CG_Cvar_Get(const char *cvar) {
	char buff[128];

	memset( buff, 0, sizeof( buff ) );
	trap_Cvar_VariableStringBuffer( cvar, buff, sizeof( buff ) );
	return atof( buff );
}

void CG_Text_PaintWithCursor(float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style) {
	CG_Text_Paint( x, y, scale, color, text, 0, limit, style );
}

/*
=============
CG_LevelTimerWidth

Returns the width of the level timer string for layout calculations.
=============
*/
static int CG_LevelTimerWidth( float scale ) {
	char buffer[32];
	int msec;
	int seconds;

	msec = cg.time - cgs.levelStartTime;
	if ( msec < 0 ) {
	msec = 0;
	}

	seconds = msec / 1000;
	Com_sprintf( buffer, sizeof( buffer ), "%02i:%02i", seconds / 60, seconds % 60 );

	return CG_Text_Width( buffer, scale, 0 );
}

/*
=============
CG_RoundLabelWidth

Returns the width of the current match state label.
=============
*/
static int CG_RoundLabelWidth( float scale ) {
	char buffer[32];
	const char *label;

	if ( cgs.matchTimeoutActive ) {
	label = "Timeout";
	} else if ( cgs.matchOvertimeActive ) {
	label = "Overtime";
	} else if ( cg.snap && cg.snap->ps.pm_type == PM_INTERMISSION ) {
	label = "Intermission";
	} else if ( cgs.matchRoundState == ROUNDSTATE_WARMUP || cg.warmup > 0 ) {
	label = "Warmup";
	} else if ( cgs.matchRoundState == ROUNDSTATE_COMPLETE ) {
	label = "Round complete";
	} else if ( cgs.matchRoundNumber > 0 ) {
	Com_sprintf( buffer, sizeof( buffer ), "Round %i", cgs.matchRoundNumber );
	label = buffer;
	} else {
	label = "In progress";
	}

	return CG_Text_Width( label, scale, 0 );
}

static int CG_OwnerDrawWidth(int ownerDraw, float scale) {
	switch ( ownerDraw ) {
	case CG_GAME_TYPE:
		return CG_Text_Width( CG_GameTypeString(), scale, 0 );
	case CG_GAME_STATUS:
		return CG_Text_Width( CG_GetGameStatusText(), scale, 0 );
		break;
	case CG_KILLER:
		return CG_Text_Width( CG_GetKillerText(), scale, 0 );
		break;
	case CG_LEVELTIMER:
	case CG_ROUNDTIMER:
		return CG_LevelTimerWidth( scale );
	case CG_OVERTIME:
		return ( cg.timelimitWarnings & 4 ) ? CG_Text_Width( "OVERTIME", scale, 0 ) : 0;
	case CG_ROUND:
		return CG_RoundLabelWidth( scale );
	case CG_HEALTH_COLORIZED:
	case CG_1ST_PLYR_HEALTH_ARMOR:
		return CG_Text_Width( "000 / 000", scale, 0 );
	case CG_RACE_STATUS:
		return CG_Text_Width( CG_GetRaceStatusText(), scale, 0 );
	case CG_RACE_TIMES: {
		int width = CG_Text_Width( CG_GetRaceTimesPrimaryText(), scale, 0 );
		int secondaryWidth = CG_Text_Width( CG_GetRaceTimesSecondaryText(), scale, 0 );
		if ( secondaryWidth > width ) {
			width = secondaryWidth;
		}
		return width;
	}
	case CG_RED_NAME:
		return CG_Text_Width( cg_redTeamName.string, scale, 0 );
		break;
	case CG_BLUE_NAME:
		return CG_Text_Width( cg_blueTeamName.string, scale, 0 );
		break;
	}

	return 0;
}

static int CG_PlayCinematic(const char *name, float x, float y, float w, float h) {
  return trap_CIN_PlayCinematic(name, x, y, w, h, CIN_loop);
}

static void CG_StopCinematic(int handle) {
  trap_CIN_StopCinematic(handle);
}

static void CG_DrawCinematic(int handle, float x, float y, float w, float h) {
	trap_CIN_SetExtents(handle, x, y, w, h);
	trap_CIN_DrawCinematic(handle);
}

static void CG_RunCinematicFrame(int handle) {
	trap_CIN_RunCinematic(handle);
}

static const char *cgScoreTextureNames[] = {
	"ui/assets/score/adbr.tga",
	"ui/assets/score/adtl.tga",
	"ui/assets/score/adtm.tga",
	"ui/assets/score/adtr.tga",
	"ui/assets/score/arrow.tga",
	"ui/assets/score/arrowgray.tga",
	"ui/assets/score/bg_tabmenu.tga",
	"ui/assets/score/bgfill.tga",
	"ui/assets/score/bgfill_blue.tga",
	"ui/assets/score/bgfill_red.tga",
	"ui/assets/score/blue_team_player_bar.tga",
	"ui/assets/score/btn.tga",
	"ui/assets/score/ca_score_blu.tga",
	"ui/assets/score/ca_score_red.tga",
	"ui/assets/score/dom_score_blu.tga",
	"ui/assets/score/dom_score_red.tga",
	"ui/assets/score/flagb.tga",
	"ui/assets/score/flagr.tga",
	"ui/assets/score/frame_bl.tga",
	"ui/assets/score/frame_bottom.tga",
	"ui/assets/score/frame_br.tga",
	"ui/assets/score/frame_left.tga",
	"ui/assets/score/frame_mid.tga",
	"ui/assets/score/frame_right.tga",
	"ui/assets/score/frameb.tga",
	"ui/assets/score/framebl.tga",
	"ui/assets/score/framebr.tga",
	"ui/assets/score/framel.tga",
	"ui/assets/score/framem.tga",
	"ui/assets/score/framer.tga",
	"ui/assets/score/framet.tga",
	"ui/assets/score/frametl.tga",
	"ui/assets/score/frametr.tga",
	"ui/assets/score/gradientbar2.tga",
	"ui/assets/score/gtbox.tga",
	"ui/assets/score/ink_fade_left.tga",
	"ui/assets/score/ink_fade_right.tga",
	"ui/assets/score/logo2.tga",
	"ui/assets/score/medal_assist_sm.tga",
	"ui/assets/score/medal_capture_sm.tga",
	"ui/assets/score/medal_defend_sm.tga",
	"ui/assets/score/navbarl.tga",
	"ui/assets/score/navbarm.tga",
	"ui/assets/score/navbarr.tga",
	"ui/assets/score/navfriends.tga",
	"ui/assets/score/navleft.tga",
	"ui/assets/score/navright.tga",
	"ui/assets/score/not_ready.tga",
	"ui/assets/score/ping.tga",
	"ui/assets/score/red_team_player_bar.tga",
	"ui/assets/score/rr_remaining_enemy.tga",
	"ui/assets/score/rr_remaining_team.tga",
	"ui/assets/score/sb_borderangle.tga",
	"ui/assets/score/sb_borderend.tga",
	"ui/assets/score/sb_borderline.tga",
	"ui/assets/score/sb_borderstart.tga",
	"ui/assets/score/scoreb.tga",
	"ui/assets/score/scorebl.tga",
	"ui/assets/score/scorebox.tga",
	"ui/assets/score/scorebox_blue.tga",
	"ui/assets/score/scorebox_follow.tga",
	"ui/assets/score/scorebox_red.tga",
	"ui/assets/score/scorebox_spec.tga",
	"ui/assets/score/scorebr.tga",
	"ui/assets/score/scorel.tga",
	"ui/assets/score/scorem.tga",
	"ui/assets/score/scorer.tga",
	"ui/assets/score/scoretl.tga",
	"ui/assets/score/scoretl2.tga",
	"ui/assets/score/scoretl2_blue.tga",
	"ui/assets/score/scoretl2_red.tga",
	"ui/assets/score/scoretl3.tga",
	"ui/assets/score/scoretl_blue.tga",
	"ui/assets/score/scoretl_red.tga",
	"ui/assets/score/scoretm.tga",
	"ui/assets/score/scoretm3.tga",
	"ui/assets/score/scoretr.tga",
	"ui/assets/score/scoretr3.tga",
	"ui/assets/score/specl.tga",
	"ui/assets/score/specm.tga",
	"ui/assets/score/specr.tga",
	"ui/assets/score/statsfilll.tga",
	"ui/assets/score/statsfillm.tga",
	"ui/assets/score/statsfillr.tga",
	"ui/assets/score/statsl.tga",
	"ui/assets/score/statsm.tga",
	"ui/assets/score/statsr.tga",
	"ui/assets/score/votecast_backlit.tga"
};

/*
=============
CG_RegisterScoreTextures

Registers the HUD score asset pack used by Quake Live menu scripts.
=============
*/
static void CG_RegisterScoreTextures( void ) {
	int index;
	int count = sizeof( cgScoreTextureNames ) / sizeof( cgScoreTextureNames[0] );

	for ( index = 0; index < count; index++ ) {
		trap_R_RegisterShaderNoMip( cgScoreTextureNames[index] );
	}
}

/*
=================
CG_LoadHudMenu();

=================
*/
#define CG_HUD_SCRIPT_BUFFER 4096

/*
=============
CG_HudScriptHasCompetitiveMenus

Scans the hud script for Quake Live competitive HUD menu references.
=============
*/
static qboolean CG_HudScriptHasCompetitiveMenus( const char *hudSet ) {
	fileHandle_t	f;
	int			len;
	char		buffer[CG_HUD_SCRIPT_BUFFER];

	len = trap_FS_FOpenFile( hudSet, &f, FS_READ );
	if ( len <= 0 ) {
		return qfalse;
	}

	if ( len >= CG_HUD_SCRIPT_BUFFER ) {
		len = CG_HUD_SCRIPT_BUFFER - 1;
	}

	trap_FS_Read( buffer, len, f );
	buffer[len] = '\0';
	trap_FS_FCloseFile( f );

	if ( strstr( buffer, "comp_hud" ) || strstr( buffer, "comp_spectator" ) ) {
		return qtrue;
	}

	return qfalse;
}

void CG_LoadHudMenu() {
	char buff[1024];
	const char *hudSet;

	cgDC.registerShaderNoMip = &trap_R_RegisterShaderNoMip;
	cgDC.setColor = &trap_R_SetColor;
	cgDC.drawHandlePic = &CG_DrawPic;
	cgDC.drawStretchPic = &trap_R_DrawStretchPic;
	cgDC.drawText = &CG_Text_Paint;
	cgDC.textWidth = &CG_Text_Width;
	cgDC.textHeight = &CG_Text_Height;
	cgDC.registerModel = &trap_R_RegisterModel;
	cgDC.modelBounds = &trap_R_ModelBounds;
	cgDC.fillRect = &CG_FillRect;
	cgDC.drawRect = &CG_DrawRect;   
	cgDC.drawSides = &CG_DrawSides;
	cgDC.drawTopBottom = &CG_DrawTopBottom;
	cgDC.clearScene = &trap_R_ClearScene;
	cgDC.addRefEntityToScene = &trap_R_AddRefEntityToScene;
	cgDC.renderScene = &trap_R_RenderScene;
	cgDC.registerFont = &trap_R_RegisterFont;
	cgDC.ownerDrawItem = &CG_OwnerDraw;
	cgDC.getValue = &CG_GetValue;
	cgDC.ownerDrawVisible = &CG_OwnerDrawVisible;
	cgDC.runScript = &CG_RunMenuScript;
	cgDC.getTeamColor = &CG_GetTeamColor;
	cgDC.setCVar = trap_Cvar_Set;
	cgDC.getCVarString = trap_Cvar_VariableStringBuffer;
	cgDC.getCVarValue = CG_Cvar_Get;
	cgDC.drawTextWithCursor = &CG_Text_PaintWithCursor;
	//cgDC.setOverstrikeMode = &trap_Key_SetOverstrikeMode;
	//cgDC.getOverstrikeMode = &trap_Key_GetOverstrikeMode;
	cgDC.startLocalSound = &trap_S_StartLocalSound;
	cgDC.ownerDrawHandleKey = &CG_OwnerDrawHandleKey;
	cgDC.feederCount = &CG_FeederCount;
	cgDC.feederItemImage = &CG_FeederItemImage;
	cgDC.feederItemText = &CG_FeederItemText;
	cgDC.feederSelection = &CG_FeederSelection;
	//cgDC.setBinding = &trap_Key_SetBinding;
	//cgDC.getBindingBuf = &trap_Key_GetBindingBuf;
	//cgDC.keynumToStringBuf = &trap_Key_KeynumToStringBuf;
	//cgDC.executeText = &trap_Cmd_ExecuteText;
	cgDC.Error = &Com_Error; 
	cgDC.Print = &Com_Printf; 
	cgDC.ownerDrawWidth = &CG_OwnerDrawWidth;
	//cgDC.Pause = &CG_Pause;
	cgDC.registerSound = &trap_S_RegisterSound;
	cgDC.startBackgroundTrack = &trap_S_StartBackgroundTrack;
	cgDC.stopBackgroundTrack = &trap_S_StopBackgroundTrack;
	cgDC.playCinematic = &CG_PlayCinematic;
	cgDC.stopCinematic = &CG_StopCinematic;
	cgDC.drawCinematic = &CG_DrawCinematic;
	cgDC.runCinematicFrame = &CG_RunCinematicFrame;

	Init_Display(&cgDC);

	Menu_Reset();

	trap_Cvar_VariableStringBuffer("cg_hudFiles", buff, sizeof(buff));
	hudSet = buff;
	if (hudSet[0] == '\0') {
		hudSet = CG_DEFAULT_HUD_FILE;
		trap_Cvar_Set("cg_hudFiles", hudSet);
	}

	cg.competitiveHudLoaded = CG_HudScriptHasCompetitiveMenus( hudSet );
	CG_LoadMenus(hudSet);
}


/*
=============
CG_AssetCache

Registers the shared UI assets used by the client game module.
=============
*/
void CG_AssetCache() {
	if ( !cgDC.Assets.fontRegistered ) {
		trap_R_RegisterFont( QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE, &cgDC.Assets.textFont );
		trap_R_RegisterFont( QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE, &cgDC.Assets.smallFont );
		trap_R_RegisterFont( QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE, &cgDC.Assets.bigFont );
		cgDC.Assets.fontRegistered = qtrue;
	}
	//if (Assets.textFont == NULL) {
	//  trap_R_RegisterFont("fonts/arial.ttf", 72, &Assets.textFont);
	//}
	//Assets.background = trap_R_RegisterShaderNoMip( ASSET_BACKGROUND );
	//Com_Printf("Menu Size: %i bytes\n", sizeof(Menus));
	cgDC.Assets.gradientBar = trap_R_RegisterShaderNoMip( ASSET_GRADIENTBAR );
	cgDC.Assets.fxBasePic = trap_R_RegisterShaderNoMip( ART_FX_BASE );
	cgDC.Assets.fxPic[0] = trap_R_RegisterShaderNoMip( ART_FX_RED );
	cgDC.Assets.fxPic[1] = trap_R_RegisterShaderNoMip( ART_FX_YELLOW );
	cgDC.Assets.fxPic[2] = trap_R_RegisterShaderNoMip( ART_FX_GREEN );
	cgDC.Assets.fxPic[3] = trap_R_RegisterShaderNoMip( ART_FX_TEAL );
	cgDC.Assets.fxPic[4] = trap_R_RegisterShaderNoMip( ART_FX_BLUE );
	cgDC.Assets.fxPic[5] = trap_R_RegisterShaderNoMip( ART_FX_CYAN );
	cgDC.Assets.fxPic[6] = trap_R_RegisterShaderNoMip( ART_FX_WHITE );
	cgDC.Assets.scrollBar = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR );
	cgDC.Assets.scrollBarArrowDown = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR_ARROWDOWN );
	cgDC.Assets.scrollBarArrowUp = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR_ARROWUP );
	cgDC.Assets.scrollBarArrowLeft = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR_ARROWLEFT );
	cgDC.Assets.scrollBarArrowRight = trap_R_RegisterShaderNoMip( ASSET_SCROLLBAR_ARROWRIGHT );
	cgDC.Assets.scrollBarThumb = trap_R_RegisterShaderNoMip( ASSET_SCROLL_THUMB );
	cgDC.Assets.sliderBar = trap_R_RegisterShaderNoMip( ASSET_SLIDER_BAR );
	cgDC.Assets.sliderThumb = trap_R_RegisterShaderNoMip( ASSET_SLIDER_THUMB );

	CG_RegisterScoreTextures();
}
/*
=================
CG_Init

Called after every level change or subsystem restart
Will perform callbacks to make the loading info screen update.
=================
*/
void CG_Init( int serverMessageNum, int serverCommandSequence, int clientNum ) {
	const char	*s;

	// clear everything
	memset( &cgs, 0, sizeof( cgs ) );
	memset( &cg, 0, sizeof( cg ) );
	memset( cg_entities, 0, sizeof(cg_entities) );
	memset( cg_weapons, 0, sizeof(cg_weapons) );
	memset( cg_items, 0, sizeof(cg_items) );
  
	CG_ClearAutomationState();
	cg.spectatorPrimaryClient = -1;
	cg.spectatorSecondaryClient = -1;
	cg.spectatorFollowClient = -1;
	cg.spectatorTrackedClient = -1;
	cg.trackedPlayerClientNum = -1;
	cg.trackedPlayerPriority = CG_SPECTATOR_TRACK_NONE;
	cg.trackedPlayerExpireTime = 0;
	cg.viewFilter.count = 0;
	cg.viewFilter.index = 0;
	cg.viewFilter.lastYaw = 0.0f;
	cg.viewFilter.lastPitch = 0.0f;
	CG_ParsePmoveConfigString( NULL );


	cg.clientNum = clientNum;

	cgs.processedSnapshotNum = serverMessageNum;
	cgs.serverCommandSequence = serverCommandSequence;

	// load a few needed things before we do any screen updates
	cgs.media.charsetShader		= trap_R_RegisterShader( "gfx/2d/bigchars" );
	cgs.media.whiteShader		= trap_R_RegisterShader( "white" );
	cgs.media.charsetProp		= trap_R_RegisterShaderNoMip( "menu/art/font1_prop.tga" );
	cgs.media.charsetPropGlow	= trap_R_RegisterShaderNoMip( "menu/art/font1_prop_glo.tga" );
	cgs.media.charsetPropB		= trap_R_RegisterShaderNoMip( "menu/art/font2_prop.tga" );
	cgs.media.loadingBackground	= trap_R_RegisterShaderNoMip( "levelshots/loadingback.jpg" );
	cgs.media.gameTypeBackground	= trap_R_RegisterShaderNoMip( "ui/assets/main_menu/gt_background.tga" );
	cgs.media.logoBackground	= trap_R_RegisterShaderNoMip( "ui/assets/main_menu/logo_background.tga" );
	cgs.media.qlLogo			= trap_R_RegisterShaderNoMip( "ui/assets/main_menu/ql_logo.tga" );
	cgs.media.menuSmokeShader	= trap_R_RegisterShaderNoMip( "ui/assets/backscreen_smoke.jpg" );
	cgs.media.modifiedIcon		= trap_R_RegisterShaderNoMip( "icons/modified.tga" );

	trap_Cvar_Set( "ui_mainmenu", "0" );
	trap_Cvar_Set( "ui_intermission", "0" );
	trap_Cvar_Set( "ui_warmup", "0" );

	CG_RegisterCvars();

	CG_InitConsoleCommands();

	cg.weaponSelect = WP_MACHINEGUN;

	cgs.redflag = cgs.blueflag = -1; // For compatibily, default to unset for
	cgs.flagStatus = -1;
	// old servers

	// get the rendering configuration from the client system
	trap_GetGlconfig( &cgs.glconfig );
	cgs.screenXScale = cgs.glconfig.vidWidth / 640.0;
	cgs.screenYScale = cgs.glconfig.vidHeight / 480.0;

	// get the gamestate from the client system
	trap_GetGameState( &cgs.gameState );

	// check version
	s = CG_ConfigString( CS_GAME_VERSION );
	if ( strcmp( s, GAME_VERSION ) ) {
		CG_Error( "Client/Server game mismatch: %s/%s", GAME_VERSION, s );
	}

	s = CG_ConfigString( CS_LEVEL_START_TIME );
	cgs.levelStartTime = atoi( s );

	CG_ParseServerinfo();

	// load the new map
	CG_LoadingString( "collision map" );

	trap_CM_LoadMap( cgs.mapname );

	String_Init();

	cg.loading = qtrue;		// force players to load instead of defer

	CG_LoadingString( "sounds" );

	CG_RegisterSounds();

	CG_LoadingString( "graphics" );

	CG_RegisterGraphics();

	CG_LoadingString( "clients" );

	CG_RegisterClients();		// if low on memory, some clients will be deferred

	CG_AssetCache();
	CG_LoadHudMenu();      // load new hud stuff

	cg.loading = qfalse;	// future players will be deferred

	CG_InitLocalEntities();

	CG_InitMarkPolys();

	// remove the last loading update
	cg.infoScreenText[0] = 0;

	// Make sure we have update values (scores)
	CG_SetConfigValues();

	CG_StartMusic();

	CG_LoadingString( "" );

	CG_InitTeamChat();
	CG_ReplayLastMessageFromCvar();

	CG_ShaderStateChanged();

	trap_S_ClearLoopingSounds( qtrue );
}

/*
=================
CG_Shutdown

Called before every level change or subsystem restart
=================
*/
void CG_Shutdown( void ) {
	// some mods may need to do cleanup work here,
	// like closing files or archiving session data
	CG_ClearAutomationState();
}


/*
==================
CG_EventHandling
==================
 type 0 - no event handling
      1 - team menu
      2 - hud editor

*/

