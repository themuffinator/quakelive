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
extern menuDef_t *menuScoreboard;
extern menuDef_t *menuStats;
static menuDef_t *cgScoreboardSelectionMenus[2];

#define DEFAULT_WEAPON_BAR_GRENADE_COLOR	"0x007000FF"
#define DEFAULT_SCREEN_DAMAGE_COLOR		"0x700000C8"
#define DEFAULT_SCREEN_DAMAGE_SELF_COLOR	"0x00000000"
#define DEFAULT_SCREEN_DAMAGE_TEAM_COLOR	"0x700000C8"
#define DEFAULT_SCREEN_DAMAGE_ALPHA		"200"

#define CG_AUTOACTION_MAX_RECORDINGS		1000
#define CG_AUTOACTION_SCREENSHOT_DELAY		1000
#define CG_AUTOACTION_STATS_DELAY		1500
#define CG_SPECTATOR_SLOT_TRACK_HOLD		3000

int forceModelModificationCount = -1;
int forceTeamModelModificationCount = -1;
int teamModelModificationCount = -1;
int teamColorsModificationCount = -1;
int forceTeamSkinModificationCount = -1;
int forceEnemyModelModificationCount = -1;
int enemyModelModificationCount = -1;
int enemyColorsModificationCount = -1;
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
void CG_RegisterCvars( void );
static void CG_UpdateSimpleItemsSettings( void );
static void CG_UpdateCrosshairColorSettings( void );
static void CG_UpdateCrosshairPulseSettings( void );
static void CG_UpdateCrosshairHitSettings( void );
static void CG_UpdateAutomationSettings( void );
static void CG_ClearAutomationState( void );
static qboolean CG_UseMatchSummaryChatLayout( void );
static int CG_GetPhysicsTime( void );
static float CG_GetChatFieldY( void );
static float CG_GetChatFieldPixelWidth( void );
static int CG_GetChatFieldWidthInChars( void );
static qboolean CG_CopyClientIdentity( int clientNum, void *outIdentity );
static int CG_NativeGetChatFieldY( void );
static int CG_NativeGetChatFieldPixelWidth( void );
static int CG_NativeSetClientSpeakingState( int clientNum, int speaking );
static void CG_ShowTrackedPlayerSlot( int slot );
static void CG_Show1stTrackedPlayer( void );
static void CG_Show2ndTrackedPlayer( void );
void CG_Cvar_GetString( const char *cvar, char *buffer, int bufsize );
itemDef_t *Menu_FindItemByName( menuDef_t *menu, const char *p );
void Menu_UpdatePosition( menuDef_t *menu );

/*
================
CG_NativeDrawActiveFrame

Native export wrapper for the legacy CG_DRAW_ACTIVE_FRAME entry.
================
*/
static void CG_NativeDrawActiveFrame( int serverTime, stereoFrame_t stereoView, qboolean demoPlayback ) {
	CG_DrawActiveFrame( serverTime, stereoView, demoPlayback );
}

/*
================
CG_NativeKeyEvent

Native export wrapper for the legacy CG_KEY_EVENT entry.
================
*/
static void CG_NativeKeyEvent( int key, qboolean down ) {
	CG_KeyEvent( key, down );
}


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
		CG_NativeDrawActiveFrame( arg0, arg1, arg2 ? qtrue : qfalse );
		return 0;
	case CG_CROSSHAIR_PLAYER:
		return CG_CrosshairPlayer();
	case CG_LAST_ATTACKER:
		return CG_LastAttacker();
	case CG_KEY_EVENT:
		CG_NativeKeyEvent( arg0, arg1 ? qtrue : qfalse );
		return 0;
	case CG_MOUSE_EVENT:
		cgDC.cursorx = cgs.cursorX;
		cgDC.cursory = cgs.cursorY;
		CG_MouseEvent( arg0, arg1 );
		return 0;
	case CG_EVENT_HANDLING:
		CG_EventHandling( arg0 );
		return 0;
	case CG_CHAT_DOWN:
		cg.chatHistoryVisible = qtrue;
		return 0;
	case CG_CHAT_UP:
		cg.chatHistoryVisible = qfalse;
		return 0;
	case CG_SHOW_1ST_TRACKED_PLAYER:
		CG_Show1stTrackedPlayer();
		return 0;
	case CG_SHOW_2ND_TRACKED_PLAYER:
		CG_Show2ndTrackedPlayer();
		return 0;
	case CG_COPY_CLIENT_IDENTITY:
		return CG_CopyClientIdentity( arg0, (void *)(intptr_t)arg1 );
	case CG_GET_CHAT_FIELD_Y:
		return CG_NativeGetChatFieldY();
	case CG_GET_CHAT_FIELD_PIXEL_WIDTH:
		return CG_NativeGetChatFieldPixelWidth();
	case CG_GET_CHAT_FIELD_WIDTH_IN_CHARS:
		return CG_GetChatFieldWidthInChars();
	case CG_SET_CLIENT_SPEAKING_STATE:
		return CG_NativeSetClientSpeakingState( arg0, arg1 );
	case CG_GET_PHYSICS_TIME:
		return CG_GetPhysicsTime();
	default:
		CG_Error( "vmMain: unknown command %i", command );
		break;
	}
	return -1;
}

/*
================
CG_NativeMouseEvent

Native export wrapper for the legacy CG_MOUSE_EVENT entry.
================
*/
static void CG_NativeMouseEvent( int dx, int dy ) {
	cgDC.cursorx = cgs.cursorX;
	cgDC.cursory = cgs.cursorY;
	CG_MouseEvent( dx, dy );
}

/*
================
CG_NativeChatDown

Native export wrapper for the legacy CG_CHAT_DOWN entry.
================
*/
static void CG_NativeChatDown( void ) {
	cg.chatHistoryVisible = qtrue;
}

/*
================
CG_NativeChatUp

Native export wrapper for the legacy CG_CHAT_UP entry.
================
*/
static void CG_NativeChatUp( void ) {
	cg.chatHistoryVisible = qfalse;
}

static void *cg_nativeExports[CG_NATIVE_EXPORT_COUNT] = {
	[CG_NATIVE_EXPORT_INIT] = CG_Init,
	[CG_NATIVE_EXPORT_REGISTER_CVARS] = CG_RegisterCvars,
	[CG_NATIVE_EXPORT_SHUTDOWN] = CG_Shutdown,
	[CG_NATIVE_EXPORT_CONSOLE_COMMAND] = CG_ConsoleCommand,
	[CG_NATIVE_EXPORT_DRAW_ACTIVE_FRAME] = CG_NativeDrawActiveFrame,
	[CG_NATIVE_EXPORT_CROSSHAIR_PLAYER] = CG_CrosshairPlayer,
	[CG_NATIVE_EXPORT_LAST_ATTACKER] = CG_LastAttacker,
	[CG_NATIVE_EXPORT_KEY_EVENT] = CG_NativeKeyEvent,
	[CG_NATIVE_EXPORT_MOUSE_EVENT] = CG_NativeMouseEvent,
	[CG_NATIVE_EXPORT_EVENT_HANDLING] = CG_EventHandling,
	[CG_NATIVE_EXPORT_SHOW_1ST_TRACKED_PLAYER] = CG_Show1stTrackedPlayer,
	[CG_NATIVE_EXPORT_SHOW_2ND_TRACKED_PLAYER] = CG_Show2ndTrackedPlayer,
	[CG_NATIVE_EXPORT_CHAT_DOWN] = CG_NativeChatDown,
	[CG_NATIVE_EXPORT_CHAT_UP] = CG_NativeChatUp,
	[CG_NATIVE_EXPORT_GET_PHYSICS_TIME] = CG_GetPhysicsTime,
	[CG_NATIVE_EXPORT_COPY_CLIENT_IDENTITY] = CG_CopyClientIdentity,
	[CG_NATIVE_EXPORT_RESERVED_NULL] = NULL,
	[CG_NATIVE_EXPORT_GET_CHAT_FIELD_Y] = CG_NativeGetChatFieldY,
	[CG_NATIVE_EXPORT_GET_CHAT_FIELD_PIXEL_WIDTH] = CG_NativeGetChatFieldPixelWidth,
	[CG_NATIVE_EXPORT_GET_CHAT_FIELD_WIDTH_IN_CHARS] = CG_GetChatFieldWidthInChars,
	[CG_NATIVE_EXPORT_SET_CLIENT_SPEAKING_STATE] = CG_NativeSetClientSpeakingState
};

/*
================
CG_GetNativeExportTable

Returns the Quake Live native cgame export table published by dllEntry.
================
*/
void **CG_GetNativeExportTable( void ) {
	return cg_nativeExports;
}


cg_t				cg;
cgs_t				cgs;
centity_t			cg_entities[MAX_GENTITIES];
weaponInfo_t		cg_weapons[MAX_WEAPONS];
itemInfo_t			cg_items[MAX_ITEMS];
pmove_settings_t		cg_pmoveSettings;

typedef struct {
	qboolean	speaking;
	int		time;
} cgClientSpeakingState_t;

static cgClientSpeakingState_t	cgClientSpeakingState[MAX_CLIENTS];


static int		weaponColorGrenadeModCount = -1;
static int		lowAmmoWarningPercentileModCount = -1;
static int		announcerModificationCount = -1;

vmCvar_t	cg_armorTiered;
vmCvar_t	cg_addMarks;
vmCvar_t	cg_allowTaunt;
vmCvar_t	cg_noTaunt;
vmCvar_t	cg_animSpeed;
vmCvar_t	cg_announcer;
vmCvar_t	cg_announcerRewardsVO;
vmCvar_t	cg_autoAction;
vmCvar_t	cg_autoHop;
vmCvar_t	cg_autoswitch;
vmCvar_t	cg_autoProjectileNudge;
vmCvar_t	cg_bigFont;
vmCvar_t	cg_blood;
vmCvar_t	cg_blueTeamName;
vmCvar_t	cg_bob;
vmCvar_t	cg_bobup;
vmCvar_t	cg_bobpitch;
vmCvar_t	cg_bobroll;
vmCvar_t	cg_runpitch;
vmCvar_t	cg_runroll;
vmCvar_t	cg_brassTime;
vmCvar_t	cg_bubbleTrail;
vmCvar_t	cg_buildScript;
vmCvar_t	cg_cameraMode;
vmCvar_t	cg_cameraOrbit;
vmCvar_t	cg_cameraOrbitDelay;
vmCvar_t	cg_cameraSmartMode;
vmCvar_t	cg_cameraThirdPersonSmartMode;
vmCvar_t	cg_centertime;
vmCvar_t	cg_chatbeep;
vmCvar_t	cg_chatHistoryLength;
vmCvar_t	cg_complaintWarning;
vmCvar_t	cg_playVoiceChats;
vmCvar_t	cg_showVoiceText;
vmCvar_t	cg_crosshairBrightness;
vmCvar_t	cg_crosshairColor;
vmCvar_t	cg_crosshairHealth;
vmCvar_t	cg_crosshairHitColor;
vmCvar_t	cg_crosshairHitStyle;
vmCvar_t	cg_crosshairHitTime;
vmCvar_t	cg_crosshairPulse;
vmCvar_t	cg_crosshairSize;
vmCvar_t	cg_crosshairX;
vmCvar_t	cg_crosshairY;
vmCvar_t	cg_currentSelectedPlayer;
vmCvar_t	cg_currentSelectedPlayerName;
vmCvar_t	cg_damagePlum;
vmCvar_t	cg_damagePlumColorStyle;
vmCvar_t	cg_deadBodyColor;
vmCvar_t	cg_deadBodyDarken;
vmCvar_t	cg_debugAnim;
vmCvar_t	cg_debugEvents;
vmCvar_t	cg_debugPosition;
vmCvar_t	cg_debugOwnerdrawStats;
vmCvar_t	cg_deferPlayers;
vmCvar_t	cg_disableLoadout_g;
vmCvar_t	cg_disableLoadout_mg;
vmCvar_t	cg_disableLoadout_sg;
vmCvar_t	cg_disableLoadout_gl;
vmCvar_t	cg_disableLoadout_rl;
vmCvar_t	cg_disableLoadout_lg;
vmCvar_t	cg_disableLoadout_rg;
vmCvar_t	cg_disableLoadout_pg;
vmCvar_t	cg_disableLoadout_bfg;
vmCvar_t	cg_disableLoadout_gh;
vmCvar_t	cg_disableLoadout_ng;
vmCvar_t	cg_disableLoadout_pl;
vmCvar_t	cg_disableLoadout_cg;
vmCvar_t	cg_disableLoadout_hmg;
vmCvar_t	cg_draw2D;
vmCvar_t	cg_draw3dIcons;
vmCvar_t	cg_drawAmmoWarning;
vmCvar_t	cg_drawAttacker;
vmCvar_t	cg_drawCrosshair;
vmCvar_t	cg_drawCrosshairTeamHealth;
vmCvar_t	cg_drawCrosshairTeamHealthSize;
vmCvar_t	cg_drawDeadFriendTime;
vmCvar_t	cg_drawDemoHUD;
vmCvar_t	cg_drawFPS;
vmCvar_t	cg_drawFragMessages;
vmCvar_t	cg_drawFullWeaponBar;
vmCvar_t	cg_drawGun;
vmCvar_t	cg_drawHitFriendTime;
vmCvar_t	cg_drawIcons;
vmCvar_t	cg_drawInputCmds;
vmCvar_t	cg_drawInputCmdsSize;
vmCvar_t	cg_drawInputCmdsX;
vmCvar_t	cg_drawInputCmdsY;
vmCvar_t	cg_drawItemPickups;
vmCvar_t	cg_drawPregameMessages;
vmCvar_t	cg_drawProfileImages;
vmCvar_t	cg_drawCheckpointRemaining;
vmCvar_t	cg_drawRewards;
vmCvar_t	cg_drawRewardsRowSize;
vmCvar_t	cg_drawSnapshot;
vmCvar_t	cg_drawTimer;
vmCvar_t	cg_drawSpecMessages;
vmCvar_t	cg_drawSprites;
vmCvar_t	cg_drawSpriteSelf;
vmCvar_t	cg_drawStatus;
vmCvar_t	cg_drawTeamOverlay;
vmCvar_t	cg_drawTeamOverlayOpacity;
vmCvar_t	cg_drawTeamOverlaySize;
vmCvar_t	cg_drawTeamOverlayX;
vmCvar_t	cg_drawTeamOverlayY;
vmCvar_t	cg_teamOverlayUserinfo;
vmCvar_t	cg_drawTieredArmorAvailability;
vmCvar_t	cg_enableDust;
vmCvar_t	cg_enableBreath;
vmCvar_t	cg_enemyCrosshairNames;
vmCvar_t	cg_enemyCrosshairNamesOpacity;
vmCvar_t	cg_enemyColors;
vmCvar_t	cg_enemyHeadColor;
vmCvar_t	cg_enemyLowerColor;
vmCvar_t	cg_enemyUpperColor;
vmCvar_t	cg_errorDecay;
vmCvar_t	cg_filter_angles;
vmCvar_t	cg_followKiller;
vmCvar_t	cg_followPowerup;
vmCvar_t	cg_footsteps;
vmCvar_t	cg_forceDrawCrosshair;
vmCvar_t	cg_forceModel;
vmCvar_t	cg_forceEnemyModel;
vmCvar_t	cg_enemyModel;
vmCvar_t	cg_forceEnemySkin;
vmCvar_t	cg_forceEnemyWeaponColor;
vmCvar_t	cg_forceTeamModel;
vmCvar_t	cg_teamModel;
vmCvar_t	cg_forceTeamSkin;
vmCvar_t	cg_forceTeamWeaponColor;
vmCvar_t	cg_fov;
vmCvar_t	cg_gameInfo1;
vmCvar_t	cg_gameInfo2;
vmCvar_t	cg_gameInfo3;
vmCvar_t	cg_gameInfo4;
vmCvar_t	cg_gameInfo5;
vmCvar_t	cg_gameInfo6;
vmCvar_t	cg_gametype;
vmCvar_t	cg_gun_x;
vmCvar_t	cg_gun_y;
vmCvar_t	cg_gun_z;
vmCvar_t	cg_hudFiles;
vmCvar_t	cg_ignoreMouseInput;
vmCvar_t	cg_itemTimers;
vmCvar_t	cg_kickScale;
vmCvar_t	cg_lagometer;
vmCvar_t	cg_lastmsg;
vmCvar_t	cg_levelTimerDirection;
vmCvar_t	cg_lightningImpact;
vmCvar_t	cg_lightningImpactCap;
vmCvar_t	cg_lightningStyle;
vmCvar_t	cg_loadout;
vmCvar_t	cg_lowAmmoWarningPercentile;
vmCvar_t	cg_lowAmmoWarningSound;
vmCvar_t	cg_lowAmmoWeaponBarWarning;
vmCvar_t	cg_muzzleFlash;
vmCvar_t	cg_noPlayerAnims;
vmCvar_t	cg_nopredict;
vmCvar_t	cg_synchronousClients;
vmCvar_t	cg_obeliskRespawnDelay;
vmCvar_t	cg_obituaryRowSize;
vmCvar_t	cg_overheadNamesWidth;
vmCvar_t	cg_paused;
vmCvar_t	cg_preferredStartingWeapons;
vmCvar_t	cg_plasmaStyle;
vmCvar_t	cg_playerCylinders;
vmCvar_t	cg_smoothClients;
vmCvar_t	pmove_fixed;
vmCvar_t	pmove_msec;
//vmCvar_t	cg_pmove_fixed;
vmCvar_t	cg_predictItems;
vmCvar_t	cg_predictLocalRailshots;
vmCvar_t	cg_projectileNudge;
vmCvar_t	cg_raceBeep;
vmCvar_t	cg_railStyle;
vmCvar_t	cg_railTrailTime;
vmCvar_t	cg_recordSPDemo;
vmCvar_t	cg_recordSPDemoName;
vmCvar_t	cg_redTeamName;
vmCvar_t	cg_rocketStyle;
vmCvar_t	cg_scorePlum;
vmCvar_t	cg_screenDamage;
vmCvar_t	cg_screenDamage_Self;
vmCvar_t	cg_screenDamage_Team;
vmCvar_t	cg_screenDamageAlpha;
vmCvar_t	cg_screenDamageAlpha_Team;
vmCvar_t	cg_selfOnTeamOverlay;
vmCvar_t	cg_shadows;
vmCvar_t	cg_showmiss;
vmCvar_t	cg_simpleItems;
vmCvar_t	cg_simpleItemsBob;
vmCvar_t	cg_simpleItemsHeightOffset;
vmCvar_t	cg_simpleItemsRadius;
vmCvar_t	cg_singlePlayer;
vmCvar_t	cg_singlePlayerActive;
vmCvar_t	cg_smallFont;
vmCvar_t	cg_spectating;
vmCvar_t	cg_specItemTimers;
vmCvar_t	cg_specItemTimersSize;
vmCvar_t	cg_specItemTimersX;
vmCvar_t	cg_specItemTimersY;
vmCvar_t	cg_specNames;
vmCvar_t	cg_specTeamVitals;
vmCvar_t	cg_specTeamVitalsHealthColor;
vmCvar_t	cg_speedometer;
vmCvar_t	cg_stats;
vmCvar_t	cg_stereoSeparation;
vmCvar_t	cg_swingSpeed;
vmCvar_t	cg_switchOnEmpty;
vmCvar_t	cg_switchToEmpty;
vmCvar_t	cg_teamChatBeep;
vmCvar_t	cg_teamChatHeight;
vmCvar_t	cg_teamChatsOnly;
vmCvar_t	cg_teamChatTime;
vmCvar_t	cg_teamColors;
vmCvar_t	cg_teamHeadColor;
vmCvar_t	cg_teamLowerColor;
vmCvar_t	cg_teamUpperColor;
vmCvar_t	cg_teammateCrosshairNames;
vmCvar_t	cg_teammateCrosshairNamesOpacity;
vmCvar_t	cg_drawFriend;
vmCvar_t	cg_teammateNames;
vmCvar_t	cg_teammatePOIs;
vmCvar_t	cg_teammatePOIsMaxWidth;
vmCvar_t	cg_teammatePOIsMinWidth;
vmCvar_t	cg_flagPOIs;
vmCvar_t	cg_powerupPOIs;
vmCvar_t	cg_poiMinWidth;
vmCvar_t	cg_poiMaxWidth;
vmCvar_t	cg_thirdPerson;
vmCvar_t	cg_thirdPersonAngle;
vmCvar_t	cg_thirdPersonPitch;
vmCvar_t	cg_thirdPersonRange;
vmCvar_t	cg_timescale;
vmCvar_t	cg_timescaleFadeEnd;
vmCvar_t	cg_timescaleFadeSpeed;
vmCvar_t	cg_tracerChance;
vmCvar_t	cg_tracerLength;
vmCvar_t	cg_tracerWidth;
vmCvar_t	cg_trackPlayer;
vmCvar_t	cg_trueLightning;
vmCvar_t	cg_trueShotgun;
vmCvar_t	cg_useItemMessage;
vmCvar_t	cg_useItemWarning;
vmCvar_t	cg_viewsize;
vmCvar_t	cg_vignette;
vmCvar_t	cg_voiceChatIndicator;
vmCvar_t	cg_waterWarp;
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
vmCvar_t	cg_zoomFov;
vmCvar_t	cg_zoomOutOnDeath;
vmCvar_t	cg_zoomScaling;
vmCvar_t	cg_zoomSensitivity;
vmCvar_t	cg_zoomToggle;

typedef struct {
	vmCvar_t	*vmCvar;
	const char	*cvarName;
	const char	*defaultString;
	int			cvarFlags;
	const char	*minimumString;
	const char	*maximumString;
} cvarTable_t;

int CG_StartingWeaponIndexFromToken( const char *value );
static unsigned int CG_ParseDamagePlumWeaponMask( const char *value );
static damagePlumPreset_t CG_ClassifyDamagePlumPreset( const char *value, unsigned int mask );
static damagePlumColorStyle_t CG_ParseDamagePlumColorStyleValue( int rawValue );
static void CG_UpdateDamagePlumSettings( void );
static const char *CG_RetailAnnouncerFolderForProfile( cgAnnouncerProfile_t profile );
static sfxHandle_t CG_RegisterConfiguredAnnouncerClip( const char *sample );
static sfxHandle_t CG_RegisterRetailAnnouncerClip( cgAnnouncerProfile_t profile, const char *sample );
static sfxHandle_t CG_RegisterAnnouncerClip( const char *folder, const char *sample );
static void CG_RegisterPowerupAnnouncerSounds( void );
static void CG_RegisterAnnouncerVoiceSet( cgAnnouncerProfile_t profile, const char *folder );
static sfxHandle_t CG_RegisterRaceCueSound( const char *name );
static void CG_SetActiveAnnouncerProfile( cgAnnouncerProfile_t profile );
static void CG_UpdateAnnouncerProfileFromCvar( qboolean force );
static qboolean CG_ParseLastMessageValue( const char *value, int *timestamp, char *message, int messageSize );
static void CG_WriteLastMessageCvar( int timestamp, const char *message );
static void CG_ReplayLastMessageFromCvar( void );

static cvarTable_t cvarTable[] = { // bk001129
	{ &cg_armorTiered, "cg_armorTiered", "1", CVAR_ARCHIVE },
	{ &cg_addMarks, "cg_marks", "1", CVAR_ARCHIVE },
	{ &cg_allowTaunt, "cg_allowTaunt", "1", CVAR_ARCHIVE },
	{ &cg_noTaunt, "cg_noTaunt", "0", CVAR_ARCHIVE},
	{ &cg_animSpeed, "cg_animspeed", "1", CVAR_CHEAT },
	{ &cg_announcer, "cg_announcer", "1", CVAR_ARCHIVE },
	{ &cg_announcerRewardsVO, "cg_announcerRewardsVO", "1", CVAR_ARCHIVE },
	{ &cg_autoAction, "cg_autoAction", "0", CVAR_ARCHIVE | CVAR_LATCH },
	{ &cg_autoHop, "cg_autoHop", "1", CVAR_ARCHIVE | CVAR_LATCH },
	{ &cg_autoswitch, "cg_autoswitch", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_autoProjectileNudge, "cg_autoProjectileNudge", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_bigFont, "ui_bigFont", "0.4", CVAR_ARCHIVE},
	{ &cg_blood, "com_blood", "1", CVAR_ARCHIVE },
	{ &cg_blueTeamName, "g_blueteam", DEFAULT_BLUETEAM_NAME, CVAR_ARCHIVE },
	{ &cg_bob, "cg_bob", "1", CVAR_ARCHIVE },
	{ &cg_bobup , "cg_bobup", "0.005", CVAR_CHEAT },
	{ &cg_bobpitch, "cg_bobpitch", "0.002", CVAR_ARCHIVE },
	{ &cg_bobroll, "cg_bobroll", "0.002", CVAR_ARCHIVE },
	{ &cg_runpitch, "cg_runpitch", "0.002", CVAR_ARCHIVE},
	{ &cg_runroll, "cg_runroll", "0.005", CVAR_ARCHIVE },
	{ &cg_brassTime, "cg_brassTime", "2500", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "10000" },
	{ &cg_bubbleTrail, "cg_bubbleTrail", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_buildScript, "com_build", "0", 0 },	// force loading of all possible data amd error on failures
	{ &cg_cameraMode, "com_cameraMode", "0", CVAR_CHEAT},
	{ &cg_cameraOrbit, "cg_cameraOrbit", "0", CVAR_CHEAT},
	{ &cg_cameraOrbitDelay, "cg_cameraOrbitDelay", "50", CVAR_ARCHIVE},
	{ &cg_cameraSmartMode, "cg_cameraSmartMode", "0", CVAR_CHEAT},
	{ &cg_cameraThirdPersonSmartMode, "cg_cameraThirdPersonSmartMode", "1", CVAR_CHEAT},
	{ &cg_centertime, "cg_centertime", "3", CVAR_CHEAT },
	{ &cg_chatbeep, "cg_chatbeep", "1", CVAR_ARCHIVE },
	{ &cg_chatHistoryLength, "cg_chatHistoryLength", "0", CVAR_ARCHIVE },
	{ &cg_complaintWarning, "cg_complaintWarning", "1", CVAR_ARCHIVE },
	{ &cg_playVoiceChats, "cg_playVoiceChats", "1", CVAR_ARCHIVE },
	{ &cg_showVoiceText, "cg_showVoiceText", "1", CVAR_ARCHIVE },
	{ &cg_crosshairBrightness, "cg_crosshairBrightness", "1.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0.0", "1.0" },
	{ &cg_crosshairColor, "cg_crosshairColor", "25", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "1", "26" },
	{ &cg_crosshairHealth, "cg_crosshairHealth", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_crosshairHitColor, "cg_crosshairHitColor", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "1", "26" },
	{ &cg_crosshairHitStyle, "cg_crosshairHitStyle", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "8" },
	{ &cg_crosshairHitTime, "cg_crosshairHitTime", "200.0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0.0", "1000.0" },
	{ &cg_crosshairPulse, "cg_crosshairPulse", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_crosshairSize, "cg_crosshairSize", "32", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "320" },
	{ &cg_crosshairX, "cg_crosshairX", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "-320", "320" },
	{ &cg_crosshairY, "cg_crosshairY", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "-240", "240" },
	{ &cg_currentSelectedPlayer, "cg_currentSelectedPlayer", "0", CVAR_ARCHIVE},
	{ &cg_currentSelectedPlayerName, "cg_currentSelectedPlayerName", "", CVAR_ARCHIVE},
	{ &cg_damagePlum, "cg_damagePlum", "g mg sg gl rl lg rg pg bfg gh cg ng pl hmg", CVAR_USERINFO | CVAR_ARCHIVE },
	{ &cg_damagePlumColorStyle, "cg_damagePlumColorStyle", "1", CVAR_ARCHIVE },
	{ &cg_deadBodyColor, "cg_deadBodyColor", "0x333333ff", CVAR_ARCHIVE },
	{ &cg_deadBodyDarken, "cg_deadBodyDarken", "1", CVAR_ARCHIVE },
	{ &cg_debugAnim, "cg_debuganim", "0", CVAR_CHEAT },
	{ &cg_debugEvents, "cg_debugevents", "0", CVAR_CHEAT },
	{ &cg_debugPosition, "cg_debugposition", "0", CVAR_CHEAT },
	{ &cg_debugOwnerdrawStats, "cg_debugOwnerdrawStats", "0", CVAR_ARCHIVE },
	{ &cg_deferPlayers, "cg_deferPlayers", "0", CVAR_ARCHIVE },
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
	{ &cg_draw2D, "cg_draw2D", "1", CVAR_ARCHIVE  },
	{ &cg_draw3dIcons, "cg_draw3dIcons", "1", CVAR_ARCHIVE  },
	{ &cg_drawAmmoWarning, "cg_drawAmmoWarning", "1", CVAR_ARCHIVE  },
	{ &cg_drawAttacker, "cg_drawAttacker", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_drawCrosshair, "cg_drawCrosshair", "2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "29" },
	{ &cg_drawCrosshairTeamHealth, "cg_drawCrosshairTeamHealth", "2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "2" },
	{ &cg_drawCrosshairTeamHealthSize, "cg_drawCrosshairTeamHealthSize", "0.12", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0.10", "0.26" },
	{ &cg_drawDeadFriendTime, "cg_drawDeadFriendTime", "3000", CVAR_ARCHIVE },
	{ &cg_drawDemoHUD, "cg_drawDemoHUD", "1", CVAR_ARCHIVE },
	{ &cg_drawFPS, "cg_drawFPS", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_drawFragMessages, "cg_drawFragMessages", "1", CVAR_ARCHIVE },
	{ &cg_drawFullWeaponBar, "cg_drawFullWeaponBar", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_drawGun, "cg_drawGun", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "3" },
	{ &cg_drawHitFriendTime, "cg_drawHitFriendTime", "5000", CVAR_ARCHIVE },
	{ &cg_drawIcons, "cg_drawIcons", "1", CVAR_ARCHIVE  },
	{ &cg_drawInputCmds, "cg_drawInputCmds", "0", CVAR_ARCHIVE },
	{ &cg_drawInputCmdsSize, "cg_drawInputCmdsSize", "16", CVAR_ARCHIVE },
	{ &cg_drawInputCmdsX, "cg_drawInputCmdsX", "640", CVAR_ARCHIVE },
	{ &cg_drawInputCmdsY, "cg_drawInputCmdsY", "480", CVAR_ARCHIVE },
	{ &cg_drawItemPickups, "cg_drawItemPickups", "5", CVAR_ARCHIVE },
	{ &cg_drawPregameMessages, "cg_drawPregameMessages", "1", CVAR_ARCHIVE },
	{ &cg_drawProfileImages, "cg_drawProfileImages", "1", CVAR_ARCHIVE },
	{ &cg_drawCheckpointRemaining, "cg_drawCheckpointRemaining", "1", CVAR_ARCHIVE },
	{ &cg_drawRewards, "cg_drawRewards", "1", CVAR_ARCHIVE },
	{ &cg_drawRewardsRowSize, "cg_drawRewardsRowSize", "9", CVAR_ARCHIVE },
	{ &cg_drawSnapshot, "cg_drawSnapshot", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "2" },
	{ &cg_drawTimer, "cg_drawTimer", "0", CVAR_ARCHIVE  },
	{ &cg_drawSpecMessages, "cg_drawSpecMessages", "1", CVAR_ARCHIVE },
	{ &cg_drawSprites, "cg_drawSprites", "1", CVAR_ARCHIVE },
	{ &cg_drawSpriteSelf, "cg_drawSpriteSelf", "0", CVAR_ARCHIVE },
	{ &cg_drawStatus, "cg_drawStatus", "1", CVAR_ARCHIVE  },
	{ &cg_drawTeamOverlay, "cg_drawTeamOverlay", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "3" },
	{ &cg_drawTeamOverlayOpacity, "cg_drawTeamOverlayOpacity", "0.75", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_drawTeamOverlaySize, "cg_drawTeamOverlaySize", "0.16", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0.12", "0.22" },
	{ &cg_drawTeamOverlayX, "cg_drawTeamOverlayX", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "-640", "640" },
	{ &cg_drawTeamOverlayY, "cg_drawTeamOverlayY", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "-480", "480" },
	{ &cg_teamOverlayUserinfo, "teamoverlay", "0", CVAR_ROM | CVAR_USERINFO },
	{ &cg_drawTieredArmorAvailability, "cg_drawTieredArmorAvailability", "1", CVAR_ARCHIVE },
	{ &cg_enableDust, "g_enableDust", "0", CVAR_SERVERINFO},
	{ &cg_enableBreath, "g_enableBreath", "0", CVAR_SERVERINFO},
	{ &cg_enemyCrosshairNames, "cg_enemyCrosshairNames", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_enemyCrosshairNamesOpacity, "cg_enemyCrosshairNamesOpacity", "0.75", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_enemyColors, "cg_enemyColors", "", CVAR_ARCHIVE },
	{ &cg_enemyHeadColor, "cg_enemyHeadColor", "", CVAR_ARCHIVE },
	{ &cg_enemyLowerColor, "cg_enemyLowerColor", "", CVAR_ARCHIVE },
	{ &cg_enemyUpperColor, "cg_enemyUpperColor", "", CVAR_ARCHIVE },
	{ &cg_errorDecay, "cg_errordecay", "100", 0 },
	{ &cg_filter_angles, "cg_filter_angles", "0", CVAR_ARCHIVE },
	{ &cg_followKiller, "cg_followKiller", "0", CVAR_ARCHIVE },
	{ &cg_followPowerup, "cg_followPowerup", "0", CVAR_ARCHIVE },
	{ &cg_footsteps, "cg_footsteps", "1", CVAR_CHEAT },
	{ &cg_forceDrawCrosshair, "cg_forceDrawCrosshair", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_forceModel, "cg_forceModel", "0", CVAR_ARCHIVE  },
	{ &cg_forceEnemyModel, "cg_forceEnemyModel", "", CVAR_ARCHIVE },
	{ &cg_enemyModel, "cg_enemyModel", "", CVAR_ARCHIVE },
	{ &cg_forceEnemySkin, "cg_forceEnemySkin", "", CVAR_ARCHIVE },
	{ &cg_forceEnemyWeaponColor, "cg_forceEnemyWeaponColor", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_forceTeamModel, "cg_forceTeamModel", "", CVAR_ARCHIVE },
	{ &cg_teamModel, "cg_teamModel", "", CVAR_ARCHIVE },
	{ &cg_forceTeamSkin, "cg_forceTeamSkin", "", CVAR_ARCHIVE },
	{ &cg_forceTeamWeaponColor, "cg_forceTeamWeaponColor", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_fov, "cg_fov", "90", CVAR_ARCHIVE },
	{ &cg_gameInfo1, "cg_gameInfo1", "", CVAR_ROM },
	{ &cg_gameInfo2, "cg_gameInfo2", "", CVAR_ROM },
	{ &cg_gameInfo3, "cg_gameInfo3", "", CVAR_ROM },
	{ &cg_gameInfo4, "cg_gameInfo4", "", CVAR_ROM },
	{ &cg_gameInfo5, "cg_gameInfo5", "", CVAR_ROM },
	{ &cg_gameInfo6, "cg_gameInfo6", "", CVAR_ROM },
	{ &cg_gametype, "cg_gametype", "0", CVAR_ROM },
	{ &cg_gun_x, "cg_gunX", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "-10", "10" },
	{ &cg_gun_y, "cg_gunY", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "-10", "20" },
	{ &cg_gun_z, "cg_gunZ", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "-8", "0" },
	{ &cg_hudFiles, "cg_hudFiles", "ui/hud.txt", CVAR_ARCHIVE},
	{ &cg_ignoreMouseInput, "cg_ignoreMouseInput", "0", CVAR_ARCHIVE },
	{ &cg_itemTimers, "cg_itemTimers", "1", CVAR_ARCHIVE },
	{ &cg_kickScale, "cg_kickScale", "1", CVAR_ARCHIVE },
	{ &cg_lagometer, "cg_lagometer", "1", CVAR_ARCHIVE },
	{ &cg_lastmsg, "cg_lastmsg", "0", CVAR_ARCHIVE },
	{ &cg_levelTimerDirection, "cg_levelTimerDirection", "1", CVAR_ARCHIVE },
	{ &cg_lightningImpact, "cg_lightningImpact", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_lightningImpactCap, "cg_lightningImpactCap", "192", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "768" },
	{ &cg_lightningStyle, "cg_lightningStyle", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "1", "5" },
	{ &cg_loadout, "cg_loadout", "0", CVAR_ROM },
	{ &cg_lowAmmoWarningPercentile, "cg_lowAmmoWarningPercentile", "0.20", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0.01", "1.00" },
	{ &cg_lowAmmoWarningSound, "cg_lowAmmoWarningSound", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "2" },
	{ &cg_lowAmmoWeaponBarWarning, "cg_lowAmmoWeaponBarWarning", "2", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "2" },
	{ &cg_muzzleFlash, "cg_muzzleFlash", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_noPlayerAnims, "cg_noplayeranims", "0", CVAR_CHEAT },
	{ &cg_nopredict, "cg_nopredict", "0", 0 },
	{ &cg_synchronousClients, "g_synchronousClients", "0", 0 },	// communicated by systeminfo
	{ &cg_obeliskRespawnDelay, "g_obeliskRespawnDelay", "10", CVAR_SERVERINFO},
	{ &cg_obituaryRowSize, "cg_obituaryRowSize", "5", CVAR_ARCHIVE },
	{ &cg_overheadNamesWidth, "cg_overheadNamesWidth", "120", CVAR_ARCHIVE },
	{ &cg_paused, "cl_paused", "0", CVAR_ROM },
	{ &cg_preferredStartingWeapons, "cg_preferredStartingWeapons", "", 0x00080801 },
	{ &cg_plasmaStyle, "cg_plasmaStyle", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "1", "2" },
	{ &cg_playerCylinders, "cg_playerCylinders", "0", CVAR_ROM },
	{ &cg_smoothClients, "cg_smoothClients", "0", CVAR_USERINFO | CVAR_ARCHIVE},
	{ &pmove_fixed, "pmove_fixed", "0", 0},
	{ &pmove_msec, "pmove_msec", "8", 0},
	{ &cg_predictItems, "cg_predictItems", "1", CVAR_ARCHIVE },
	{ &cg_predictLocalRailshots, "cg_predictLocalRailshots", "1", 0 },
	{ &cg_projectileNudge, "cg_projectileNudge", "0", CVAR_CHEAT },
	{ &cg_raceBeep, "cg_raceBeep", "1", CVAR_ARCHIVE },
	{ &cg_railStyle, "cg_railStyle", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "1", "2" },
	{ &cg_railTrailTime, "cg_railTrailTime", "2000", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "2000" },
	{ &cg_recordSPDemo, "ui_recordSPDemo", "0", CVAR_ARCHIVE},
	{ &cg_recordSPDemoName, "ui_recordSPDemoName", "", CVAR_ARCHIVE},
	{ &cg_redTeamName, "g_redteam", DEFAULT_REDTEAM_NAME, CVAR_ARCHIVE },
	{ &cg_rocketStyle, "cg_rocketStyle", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "1", "2" },
	{ &cg_scorePlum, "cg_scorePlums", "1", CVAR_USERINFO | CVAR_ARCHIVE},
	{ &cg_screenDamage, "cg_screenDamage", DEFAULT_SCREEN_DAMAGE_COLOR, CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD },
	{ &cg_screenDamage_Self, "cg_screenDamage_Self", DEFAULT_SCREEN_DAMAGE_SELF_COLOR, CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD },
	{ &cg_screenDamage_Team, "cg_screenDamage_Team", DEFAULT_SCREEN_DAMAGE_TEAM_COLOR, CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD },
	{ &cg_screenDamageAlpha, "cg_screenDamageAlpha", DEFAULT_SCREEN_DAMAGE_ALPHA, CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD },
	{ &cg_screenDamageAlpha_Team, "cg_screenDamageAlpha_Team", DEFAULT_SCREEN_DAMAGE_ALPHA, CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD },
	{ &cg_selfOnTeamOverlay, "cg_selfOnTeamOverlay", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_shadows, "cg_shadows", "1", CVAR_ARCHIVE  },
	{ &cg_showmiss, "cg_showmiss", "0", 0 },
	{ &cg_simpleItems, "cg_simpleItems", "0", CVAR_ARCHIVE },
	{ &cg_simpleItemsBob, "cg_simpleItemsBob", "0", CVAR_ARCHIVE },
	{ &cg_simpleItemsHeightOffset, "cg_simpleItemsHeightOffset", "0", CVAR_ARCHIVE },
	{ &cg_simpleItemsRadius, "cg_simpleItemsRadius", "14", CVAR_ARCHIVE },
	{ &cg_singlePlayer, "ui_singlePlayerActive", "0", CVAR_USERINFO},
	{ &cg_singlePlayerActive, "ui_singlePlayerActive", "0", CVAR_USERINFO},
	{ &cg_smallFont, "ui_smallFont", "0.25", CVAR_ARCHIVE},
	{ &cg_spectating, "cg_spectating", "0", CVAR_ROM },
	{ &cg_specItemTimers, "cg_specItemTimers", "1", CVAR_ARCHIVE },
	{ &cg_specItemTimersSize, "cg_specItemTimersSize", "0.24", CVAR_ARCHIVE },
	{ &cg_specItemTimersX, "cg_specItemTimersX", "0", CVAR_ARCHIVE },
	{ &cg_specItemTimersY, "cg_specItemTimersY", "0", CVAR_ARCHIVE },
	{ &cg_specNames, "cg_specNames", "1", CVAR_ARCHIVE },
	{ &cg_specTeamVitals, "cg_specTeamVitals", "1", CVAR_ARCHIVE },
	{ &cg_specTeamVitalsHealthColor, "cg_specTeamVitalsHealthColor", "0", CVAR_ARCHIVE },
	{ &cg_speedometer, "cg_speedometer", "0", CVAR_ARCHIVE },
	{ &cg_stats, "cg_stats", "0", 0 },
	{ &cg_stereoSeparation, "cg_stereoSeparation", "0.4", CVAR_ARCHIVE  },
	{ &cg_swingSpeed, "cg_swingSpeed", "0.3", CVAR_CHEAT },
	{ &cg_switchOnEmpty, "cg_switchOnEmpty", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_switchToEmpty, "cg_switchToEmpty", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_teamChatBeep, "cg_teamChatBeep", "1", CVAR_ARCHIVE },
	{ &cg_teamChatHeight, "cg_teamChatHeight", "0", CVAR_ARCHIVE  },
	{ &cg_teamChatsOnly, "cg_teamChatsOnly", "0", CVAR_ARCHIVE },
	{ &cg_teamChatTime, "cg_teamChatTime", "3000", CVAR_ARCHIVE  },
	{ &cg_teamColors, "cg_teamColors", "", CVAR_ARCHIVE },
	{ &cg_teamHeadColor, "cg_teamHeadColor", "", CVAR_ARCHIVE },
	{ &cg_teamLowerColor, "cg_teamLowerColor", "", CVAR_ARCHIVE },
	{ &cg_teamUpperColor, "cg_teamUpperColor", "", CVAR_ARCHIVE },
	{ &cg_teammateCrosshairNames, "cg_teammateCrosshairNames", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_teammateCrosshairNamesOpacity, "cg_teammateCrosshairNamesOpacity", "0.75", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_drawFriend, "cg_drawFriend", "1", CVAR_ARCHIVE },
	{ &cg_teammateNames, "cg_teammateNames", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "2" },
	{ &cg_teammatePOIs, "cg_teammatePOIs", "1", CVAR_ARCHIVE },
	{ &cg_teammatePOIsMaxWidth, "cg_teammatePOIsMaxWidth", "24.0", CVAR_ARCHIVE },
	{ &cg_teammatePOIsMinWidth, "cg_teammatePOIsMinWidth", "4.0", CVAR_ARCHIVE },
	{ &cg_flagPOIs, "cg_flagPOIs", "1", CVAR_ARCHIVE },
	{ &cg_powerupPOIs, "cg_powerupPOIs", "2", CVAR_ARCHIVE },
	{ &cg_poiMinWidth, "cg_poiMinWidth", "16.0", CVAR_ARCHIVE },
	{ &cg_poiMaxWidth, "cg_poiMaxWidth", "32.0", CVAR_ARCHIVE },
	{ &cg_thirdPerson, "cg_thirdPerson", "0", 0 },
	{ &cg_thirdPersonAngle, "cg_thirdPersonAngle", "0", CVAR_CHEAT },
	{ &cg_thirdPersonPitch, "cg_thirdPersonPitch", "4.0", CVAR_CHEAT },
	{ &cg_thirdPersonRange, "cg_thirdPersonRange", "40", CVAR_CHEAT },
	{ &cg_timescale, "timescale", "1", 0},
	{ &cg_timescaleFadeEnd, "cg_timescaleFadeEnd", "1", 0},
	{ &cg_timescaleFadeSpeed, "cg_timescaleFadeSpeed", "0", 0},
	{ &cg_tracerChance, "cg_tracerchance", "0.4", CVAR_CHEAT },
	{ &cg_tracerLength, "cg_tracerlength", "100", CVAR_CHEAT },
	{ &cg_tracerWidth, "cg_tracerwidth", "1", CVAR_CHEAT },
	{ &cg_trackPlayer, "cg_trackPlayer", "-1", CVAR_CHEAT },
	{ &cg_trueLightning, "cg_trueLightning", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_trueShotgun, "cg_trueShotgun", "0", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "1" },
	{ &cg_useItemMessage, "cg_useItemMessage", "1", CVAR_ARCHIVE },
	{ &cg_useItemWarning, "cg_useItemWarning", "1", CVAR_ARCHIVE },
	{ &cg_viewsize, "cg_viewsize", "100", CVAR_ARCHIVE },
	// Retail defaults this on, but the current renderer path treats the black
	// PNG vignette as too opaque until shader/PNG alpha parity is restored.
	{ &cg_vignette, "cg_vignette", "0", CVAR_ARCHIVE },
	{ &cg_voiceChatIndicator, "cg_voiceChatIndicator", "1", CVAR_ARCHIVE },
	{ &cg_waterWarp, "cg_waterWarp", "1", CVAR_ARCHIVE },
	{ &cg_weaponBar, "cg_weaponBar", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "4" },
	{ &cg_weaponColor_grenade, "cg_weaponColor_grenade", DEFAULT_WEAPON_BAR_GRENADE_COLOR, CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig, "cg_weaponConfig", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_g, "cg_weaponConfig_g", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_mg, "cg_weaponConfig_mg", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_sg, "cg_weaponConfig_sg", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_gl, "cg_weaponConfig_gl", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_rl, "cg_weaponConfig_rl", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_lg, "cg_weaponConfig_lg", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_rg, "cg_weaponConfig_rg", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_pg, "cg_weaponConfig_pg", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_bfg, "cg_weaponConfig_bfg", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_gh, "cg_weaponConfig_gh", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_ng, "cg_weaponConfig_ng", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_pl, "cg_weaponConfig_pl", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_cg, "cg_weaponConfig_cg", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponConfig_hmg, "cg_weaponConfig_hmg", "", CVAR_ARCHIVE | CVAR_VM_CREATED | CVAR_CLOUD },
	{ &cg_weaponPrimary, "cg_weaponPrimary", "", CVAR_ROM },
	{ &cg_weaponPrimaryQueued, "cg_weaponPrimaryQueued", "", CVAR_TEMP },
	{ &cg_zoomFov, "cg_zoomfov", "22.5", CVAR_ARCHIVE },
	{ &cg_zoomOutOnDeath, "cg_zoomOutOnDeath", "0", CVAR_ARCHIVE },
	{ &cg_zoomScaling, "cg_zoomScaling", "1", CVAR_ARCHIVE },
	{ &cg_zoomSensitivity, "cg_zoomSensitivity", "1", CVAR_ARCHIVE },
	{ &cg_zoomToggle, "cg_zoomToggle", "0", CVAR_ARCHIVE },
	//	{ &cg_pmove_fixed, "cg_pmove_fixed", "0", CVAR_USERINFO | CVAR_ARCHIVE }
};

#define DAMAGE_PLUM_WEAPON_BIT( index ) ( 1u << ( index ) )
#define DAMAGE_PLUM_ALL_WEAPONS_MASK	0x7ffeu
#define DAMAGE_PLUM_AOE_WEAPONS_MASK ( \
	DAMAGE_PLUM_WEAPON_BIT( 3 ) | \
	DAMAGE_PLUM_WEAPON_BIT( 4 ) | \
	DAMAGE_PLUM_WEAPON_BIT( 5 ) | \
	DAMAGE_PLUM_WEAPON_BIT( 8 ) | \
	DAMAGE_PLUM_WEAPON_BIT( 9 ) )
#define CG_RETAIL_WEAPON_TOKEN_COUNT	14

typedef struct cgRetailWeaponToken_s {
	const char		*token;
	weapon_t	weapon;
	int		index;
} cgRetailWeaponToken_t;

static const cgRetailWeaponToken_t cgRetailWeaponTokens[CG_RETAIL_WEAPON_TOKEN_COUNT] = {
	{ "g", WP_GAUNTLET, 1 },
	{ "mg", WP_MACHINEGUN, 2 },
	{ "sg", WP_SHOTGUN, 3 },
	{ "gl", WP_GRENADE_LAUNCHER, 4 },
	{ "rl", WP_ROCKET_LAUNCHER, 5 },
	{ "lg", WP_LIGHTNING, 6 },
	{ "rg", WP_RAILGUN, 7 },
	{ "pg", WP_PLASMAGUN, 8 },
	{ "bfg", WP_BFG, 9 },
	{ "gh", WP_GRAPPLING_HOOK, 10 },
	{ "ng", WP_NAILGUN, 11 },
	{ "pl", WP_PROX_LAUNCHER, 12 },
	{ "cg", WP_CHAINGUN, 13 },
	{ "hmg", WP_HEAVY_MACHINEGUN, 14 }
};

/*
=============
CG_RetailWeaponTokenForToken

Resolves a retail weapon token against the fixed retail weapon-index table.
=============
*/
static const cgRetailWeaponToken_t *CG_RetailWeaponTokenForToken( const char *token ) {
	int	i;

	if ( !token || !token[0] ) {
		return NULL;
	}

	for ( i = 0; i < CG_RETAIL_WEAPON_TOKEN_COUNT; i++ ) {
		if ( !Q_stricmp( token, cgRetailWeaponTokens[i].token ) ) {
			return &cgRetailWeaponTokens[i];
		}
	}

	return NULL;
}

/*
=============
CG_DamagePlumBitForWeapon

Maps a local weapon enum onto the retail damage-plum weapon-index bit.
=============
*/
unsigned int CG_DamagePlumBitForWeapon( weapon_t weapon ) {
	int	i;

	for ( i = 0; i < CG_RETAIL_WEAPON_TOKEN_COUNT; i++ ) {
		if ( cgRetailWeaponTokens[i].weapon == weapon ) {
			return DAMAGE_PLUM_WEAPON_BIT( cgRetailWeaponTokens[i].index );
		}
	}

	return 0u;
}

/*
=============
CG_StartingWeaponIndexFromToken

Parses the queued-primary string into the retail 1-based icon-strip index.
=============
*/
int CG_StartingWeaponIndexFromToken( const char *value ) {
	char		buffer[128];
	char		*cursor;
	char		*token;
	const cgRetailWeaponToken_t	*weaponToken;

	if ( !value || !value[0] ) {
		return 0;
	}

	Q_strncpyz( buffer, value, sizeof( buffer ) );
	cursor = buffer;
	token = COM_ParseExt( &cursor, qtrue );
	if ( !token[0] ) {
		return 0;
	}

	weaponToken = CG_RetailWeaponTokenForToken( token );
	if ( weaponToken == NULL ) {
		return 0;
	}

	return weaponToken->index;
}

/*
=============
CG_ParseDamagePlumWeaponMask

Parses the cg_damagePlum string into the retail weapon-bit mask.
=============
*/
static unsigned int CG_ParseDamagePlumWeaponMask( const char *value ) {
	char buffer[MAX_CVAR_VALUE_STRING];
	char *cursor;
	char *token;
	unsigned int mask;
	int tokenCount;
	const cgRetailWeaponToken_t *weaponToken;

	if ( !value || !*value ) {
		return 0u;
	}

	Q_strncpyz( buffer, value, sizeof( buffer ) );
	cursor = buffer;
	mask = 0u;
	tokenCount = 0;

	while ( tokenCount < 16 ) {
		token = COM_ParseExt( &cursor, qtrue );
		if ( !token[0] ) {
			break;
		}

		weaponToken = CG_RetailWeaponTokenForToken( token );
		if ( weaponToken != NULL ) {
			mask |= DAMAGE_PLUM_WEAPON_BIT( weaponToken->index );
		}
		tokenCount++;
	}

	return mask;
}

/*
=============
CG_ClassifyDamagePlumPreset

Normalizes the mask-backed damage-plum configuration to a preset enum.
=============
*/
static damagePlumPreset_t CG_ClassifyDamagePlumPreset( const char *value, unsigned int mask ) {
	if ( mask == 0u ) {
		return DAMAGE_PLUM_PRESET_OFF;
	}

	if ( !Q_stricmp( value, "1" ) || !Q_stricmp( value, "on" ) || !Q_stricmp( value, "all" ) ||
		mask == DAMAGE_PLUM_ALL_WEAPONS_MASK ) {
		return DAMAGE_PLUM_PRESET_ALL_WEAPONS;
	}

	if ( !Q_stricmp( value, "2" ) || !Q_stricmp( value, "aoe" ) ||
		mask == DAMAGE_PLUM_AOE_WEAPONS_MASK ) {
		return DAMAGE_PLUM_PRESET_AOE_WEAPONS;
	}

	return DAMAGE_PLUM_PRESET_CUSTOM;
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
		unsigned int mask;

		damagePlumModificationCount = cg_damagePlum.modificationCount;
		mask = CG_ParseDamagePlumWeaponMask( cg_damagePlum.string );
		cg.damagePlumWeaponBits = mask;
		cg.damagePlumPreset = CG_ClassifyDamagePlumPreset( cg_damagePlum.string, mask );
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
CG_UnpackWeaponBarColor

Converts the retail packed RRGGBBAA cvar integer into normalized color lanes.
=============
*/
static void CG_UnpackWeaponBarColor( unsigned int packedColor, vec4_t color ) {
	color[0] = (float)( ( packedColor >> 24 ) & 0xff ) / 255.0f;
	color[1] = (float)( ( packedColor >> 16 ) & 0xff ) / 255.0f;
	color[2] = (float)( ( packedColor >> 8 ) & 0xff ) / 255.0f;
	color[3] = (float)( packedColor & 0xff ) / 255.0f;
}

/*
=============
CG_ParseWeaponBarColor

Parses the retail packed RRGGBBAA cvar value into a normalized vec4_t.
=============
*/
static qboolean CG_ParseWeaponBarColor( const char *hex, vec4_t color ) {
	char		*endPtr;
	const char	*value;
	unsigned int	packedColor;
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
		packedColor = (unsigned int)strtoul( hex, &endPtr, 0 );
		if ( endPtr == hex || *endPtr != '\0' ) {
			return qfalse;
		}

		CG_UnpackWeaponBarColor( packedColor, color );
		return qtrue;
	}

	packedColor = 0;
	for ( i = 0; i < 4; i++ ) {
		high = CG_ParseHexNibble( value[i * 2] );
		low = CG_ParseHexNibble( value[i * 2 + 1] );

		if ( high < 0 || low < 0 ) {
			return qfalse;
		}

		packedColor = ( packedColor << 8 ) | (unsigned int)( ( high << 4 ) | low );
	}

	CG_UnpackWeaponBarColor( packedColor, color );
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

Caches the low alpha byte used by screen damage effects.
=============
*/
static void CG_UpdateScreenDamageAlphaFromCvar( vmCvar_t *alphaCvar, float *target, int *modificationCount ) {
	float	alphaByte;

	alphaByte = (float)( (unsigned int)alphaCvar->integer & 0xff );
	*target = alphaByte;
	*modificationCount = alphaCvar->modificationCount;
}

/*
=================
CG_RegisterCvars

Registers the retail cgame cvar table and seeds cached derived settings.
=================
*/
void CG_RegisterCvars( void ) {
	int			i;
	cvarTable_t	*cv;
	char		var[MAX_TOKEN_CHARS];

	for ( i = 0, cv = cvarTable ; i < cvarTableSize ; i++, cv++ ) {
		if ( ( cv->cvarFlags & CVAR_VM_CREATED ) && cv->minimumString && cv->maximumString ) {
			trap_QL_Cvar_RegisterRange( cv->vmCvar, cv->cvarName,
				cv->defaultString, cv->minimumString, cv->maximumString, cv->cvarFlags );
		} else {
			trap_Cvar_Register( cv->vmCvar, cv->cvarName,
				cv->defaultString, cv->cvarFlags );
		}
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
	trap_Cvar_Register(NULL, "headmodel", DEFAULT_HEAD, CVAR_USERINFO | CVAR_ARCHIVE );
	trap_Cvar_Register(NULL, "team_model", DEFAULT_TEAM_MODEL, CVAR_USERINFO | CVAR_ARCHIVE );
	trap_Cvar_Register(NULL, "team_headmodel", DEFAULT_TEAM_HEAD, CVAR_USERINFO | CVAR_ARCHIVE );
	trap_Cvar_Register(NULL, "cg_version", Q3_VERSION, CVAR_ROM );
	trap_Cvar_Set( "ui_voteactive", "0" );
	trap_Cvar_Set( "ui_votestring", "" );

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
CG_ColorCharToIndex

Converts a character to an index into the color palette.
=============
*/
int CG_ColorCharToIndex( char ch ) {
	if ( ch >= '0' && ch <= '9' ) {
		return ch - '0';
	}
	if ( ch >= 'a' && ch <= 'z' ) {
		return 10 + ( ch - 'a' );
	}
	if ( ch >= 'A' && ch <= 'Z' ) {
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
		digit = CG_ColorCharToIndex( hex[i] );
		if ( digit < 0 || digit > 15 ) { // Strict hex check for hex strings
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
CG_GetColorForIndex

Populates a color vector using a palette-backed index.
=============
*/
void CG_GetColorForIndex( int index, vec4_t color ) {
	if ( index < 0 || index >= QL_CROSSHAIR_COLOR_COUNT ) {
		index = 0;
	}
	VectorCopy( cg_crosshairPalette[index], color );
	color[3] = 1.0f;
}

/*
=============
CG_SetCrosshairColorFromIndex

Populates a color vector using a palette-backed crosshair index.
=============
*/
static void CG_SetCrosshairColorFromIndex( int index, vec4_t color ) {
	CG_GetColorForIndex( index, color );
	if ( index < 1 || index >= QL_CROSSHAIR_COLOR_COUNT ) { // preserve original behavior of defaulting to index 1 for crosshair
		VectorCopy( cg_crosshairPalette[1], color );
	}
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
	float	clampedTime;

	if ( crosshairHitStyleModificationCount != cg_crosshairHitStyle.modificationCount ) {
		cg.crosshairHitStyle = cg_crosshairHitStyle.integer;
		crosshairHitStyleModificationCount = cg_crosshairHitStyle.modificationCount;
	}
	if ( crosshairHitTimeModificationCount != cg_crosshairHitTime.modificationCount ) {
		clampedTime = cg_crosshairHitTime.value;
		if ( clampedTime < 0.0f ) {
			clampedTime = 0.0f;
		}
		if ( clampedTime > 1000.0f ) {
			clampedTime = 1000.0f;
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

Refreshes cgame cvar mirrors and rebuilds derived state when tracked cvars move.
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
	if ( teamModelModificationCount != cg_teamModel.modificationCount ) {
		teamModelModificationCount = cg_teamModel.modificationCount;
		refreshClients = qtrue;
	}
	if ( teamColorsModificationCount != cg_teamColors.modificationCount ) {
		teamColorsModificationCount = cg_teamColors.modificationCount;
		refreshClients = qtrue;
	}
	if ( forceTeamSkinModificationCount != cg_forceTeamSkin.modificationCount ) {
		forceTeamSkinModificationCount = cg_forceTeamSkin.modificationCount;
		refreshClients = qtrue;
	}
	if ( enemyModelModificationCount != cg_enemyModel.modificationCount ) {
		enemyModelModificationCount = cg_enemyModel.modificationCount;
		refreshClients = qtrue;
	}
	if ( forceEnemyModelModificationCount != cg_forceEnemyModel.modificationCount ) {
		forceEnemyModelModificationCount = cg_forceEnemyModel.modificationCount;
		refreshClients = qtrue;
	}
	if ( enemyColorsModificationCount != cg_enemyColors.modificationCount ) {
		enemyColorsModificationCount = cg_enemyColors.modificationCount;
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
CG_PushPrintString

Mirrors the retail buffered chat writer on top of the existing timed chat ring.
=============
*/
void CG_PushPrintString( const char *text, int type, int holdTime ) {
	char		cleanText[MAX_STRING_CHARS];
	const char	*cursor;
	int		chatHeight;
	int		len;
	char		*p;
	char		*lastSpace;
	int		lastColor;
	int		messageTime;

	if ( !text ) {
		text = "";
	}

	Q_strncpyz( cleanText, text, sizeof( cleanText ) );
	len = strlen( cleanText );
	if ( len > 0 && cleanText[len - 1] == '\n' ) {
		cleanText[len - 1] = '\0';
	}

	CG_SetPrintString( type, cleanText );
	CG_WriteLastMessageCvar( cg.time, cleanText );

	if ( !cleanText[0] ) {
		return;
	}

	chatHeight = CG_GetChatHistoryLength();
	if ( chatHeight <= 0 || cg_teamChatTime.integer <= 0 ) {
		cgs.teamChatPos = 0;
		cgs.teamLastChatPos = 0;
		return;
	}

	if ( holdTime < 0 ) {
		holdTime = 0;
	}
	messageTime = cg.time + holdTime;

	cursor = cleanText;
	len = 0;
	p = cgs.teamChatMsgs[cgs.teamChatPos % chatHeight];
	*p = '\0';
	lastSpace = NULL;
	lastColor = '7';

	while ( *cursor ) {
		if ( len > TEAMCHAT_WIDTH - 1 ) {
			if ( lastSpace ) {
				cursor -= ( p - lastSpace );
				cursor++;
				p -= ( p - lastSpace );
			}
			*p = '\0';

			cgs.teamChatMsgTimes[cgs.teamChatPos % chatHeight] = messageTime;
			cgs.teamChatPos++;
			p = cgs.teamChatMsgs[cgs.teamChatPos % chatHeight];
			*p = '\0';
			*p++ = Q_COLOR_ESCAPE;
			*p++ = (char)lastColor;
			len = 0;
			lastSpace = NULL;
		}

		if ( Q_IsColorString( cursor ) ) {
			*p++ = *cursor++;
			lastColor = *cursor;
			*p++ = *cursor++;
			continue;
		}
		if ( *cursor == ' ' ) {
			lastSpace = p;
		}
		*p++ = *cursor++;
		len++;
	}
	*p = '\0';

	cgs.teamChatMsgTimes[cgs.teamChatPos % chatHeight] = messageTime;
	cgs.teamChatPos++;

	if ( cgs.teamChatPos - cgs.teamLastChatPos > chatHeight ) {
		cgs.teamLastChatPos = cgs.teamChatPos - chatHeight;
	}
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

	trap_Cvar_VariableStringBuffer( "cg_lastmsg", storedValue, sizeof( storedValue ) );
	if ( !CG_ParseLastMessageValue( storedValue, NULL, message, sizeof( message ) ) ) {
		return;
	}

	if ( message[0] ) {
		CG_PushPrintString( message, SYSTEM_PRINT, 0 );
	}
}

/*
=============
CG_ShowTrackedPlayerSlot

Arms the retail tracked-slot UI latch and replays the persisted last message.
=============
*/
static void CG_ShowTrackedPlayerSlot( int slot ) {
	if ( slot < 0 || slot > 1 ) {
		return;
	}

	cg.spectatorSlotTrackedTime[slot] = cg.time + CG_SPECTATOR_SLOT_TRACK_HOLD;
	CG_ReplayLastMessageFromCvar();
}

/*
=============
CG_Show1stTrackedPlayer

Mirrors the retail first-slot tracked-player notifier export.
=============
*/
static void CG_Show1stTrackedPlayer( void ) {
	CG_ShowTrackedPlayerSlot( 0 );
}

/*
=============
CG_Show2ndTrackedPlayer

Mirrors the retail second-slot tracked-player notifier export.
=============
*/
static void CG_Show2ndTrackedPlayer( void ) {
	CG_ShowTrackedPlayerSlot( 1 );
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

/*
=============
CG_CrosshairPlayer

Returns the active crosshair client for the recovered native export slot.
=============
*/
int CG_CrosshairPlayer( void ) {
	if ( cg.time > ( cg.crosshairClientTime + 1000 ) ) {
		return -1;
	}
	return cg.crosshairClientNum;
}

/*
=============
CG_LastAttacker

Returns the last attacker client for the recovered native export slot.
=============
*/
int CG_LastAttacker( void ) {
	if ( !cg.attackerTime ) {
		return -1;
	}
	return cg.snap->ps.persistant[PERS_ATTACKER];
}

/*
=============
CG_Printf

Formats a cgame message and forwards it through the client print trap.
=============
*/
void QDECL CG_Printf( const char *msg, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start( argptr, msg );
	vsprintf( text, msg, argptr );
	va_end( argptr );

	trap_Print( text );
	if ( cg_chatbeep.integer && cgs.media.talkSound ) {
		trap_S_StartLocalSound( cgs.media.talkSound, CHAN_LOCAL_SOUND );
	}
}

/*
=============
CG_Error

Formats a cgame error and forwards it through the client error trap.
=============
*/
void QDECL CG_Error( const char *msg, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start( argptr, msg );
	vsprintf( text, msg, argptr );
	va_end( argptr );

	trap_Error( text );
}

#ifndef CGAME_HARD_LINKED
// this is only here so the functions in q_shared.c and bg_*.c can link (FIXME)

/*
=============
Com_Error

Retail cgDC error callback wrapper that forwards directly to trap_Error.
=============
*/
void QDECL Com_Error( int level, const char *error, ... ) {
	va_list		argptr;
	char		text[1024];

	(void)level;

	va_start( argptr, error );
	vsprintf( text, error, argptr );
	va_end( argptr );

	trap_Error( text );
}

/*
=============
Com_Printf

Retail cgDC print callback wrapper that forwards directly to trap_Print.
=============
*/
void QDECL Com_Printf( const char *msg, ... ) {
	va_list		argptr;
	char		text[1024];

	va_start( argptr, msg );
	vsprintf( text, msg, argptr );
	va_end( argptr );

	trap_Print( text );
}

#endif

/*
================
CG_Argv

Returns one command argument through the recovered cgame argv wrapper.
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
CG_RetailAnnouncerFolderForProfile

Returns the retail announcer folder name used by the native cgame helper path.
============
*/
static const char *CG_RetailAnnouncerFolderForProfile( cgAnnouncerProfile_t profile ) {
	switch ( profile ) {
		case ANNOUNCER_PROFILE_DEFAULT:
			return "vo";
		case ANNOUNCER_PROFILE_VADRIGAR:
			return "vo_evil";
		case ANNOUNCER_PROFILE_DAEMIA:
			return "vo_female";
		default:
			return NULL;
	}
}

/*
============
CG_BuildAnnouncerSoundPathForProfile

Builds the retail announcer sound stem for a specific announcer profile.
============
*/
static const char *CG_BuildAnnouncerSoundPathForProfile( cgAnnouncerProfile_t profile, const char *sample ) {
	const char	*folder;

	folder = CG_RetailAnnouncerFolderForProfile( profile );
	if ( !folder || !folder[0] || !sample || !sample[0] ) {
		return NULL;
	}

	return va( "sound/%s/%s", folder, sample );
}

/*
============
CG_BuildAnnouncerSoundPath

Builds the active retail announcer sound stem from the cg_announcer cvar.
============
*/
static const char *CG_BuildAnnouncerSoundPath( const char *sample ) {
	cgAnnouncerProfile_t	profile;

	switch ( cg_announcer.integer ) {
		case 0:
			return NULL;
		case 2:
			profile = ANNOUNCER_PROFILE_VADRIGAR;
			break;
		case 3:
			profile = ANNOUNCER_PROFILE_DAEMIA;
			break;
		default:
			profile = ANNOUNCER_PROFILE_DEFAULT;
			if ( cg_announcer.integer != 1 ) {
				trap_Cvar_Set( "cg_announcer", "1" );
			}
			break;
	}

	return CG_BuildAnnouncerSoundPathForProfile( profile, sample );
}

/*
============
CG_RegisterRetailAnnouncerClip

Tries the retail announcer folder layout before broader source-side fallbacks.
============
*/
static sfxHandle_t CG_RegisterRetailAnnouncerClip( cgAnnouncerProfile_t profile, const char *sample ) {
	static const char *const exts[] = { ".ogg", ".wav" };
	const char	*pathStem;
	char		path[MAX_QPATH];
	sfxHandle_t	sfx;
	int		i;

	if ( !sample || !sample[0] ) {
		return 0;
	}
	pathStem = CG_BuildAnnouncerSoundPathForProfile( profile, sample );
	if ( !pathStem ) {
		return 0;
	}

	for ( i = 0; i < 2; i++ ) {
		Com_sprintf( path, sizeof( path ), "%s%s", pathStem, exts[i] );
		sfx = trap_S_RegisterSound( path, qtrue );
		if ( sfx ) {
			return sfx;
		}
	}

	return 0;
}

/*
============
CG_RegisterConfiguredAnnouncerClip

Registers an announcer clip for the active cg_announcer voice profile.
============
*/
static sfxHandle_t CG_RegisterConfiguredAnnouncerClip( const char *sample ) {
	const char	*path;

	if ( !sample || !sample[0] ) {
		return 0;
	}

	path = CG_BuildAnnouncerSoundPath( sample );
	if ( !path ) {
		return 0;
	}

	return trap_S_RegisterSound( path, qtrue );
}

/*
============
CG_RegisterPowerupAnnouncerSounds

Registers the active retail announcer voice clips used by powerup pickups.
============
*/
static void CG_RegisterPowerupAnnouncerSounds( void ) {
#define CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE(field, sample) \
	cgs.media.field = CG_RegisterConfiguredAnnouncerClip( sample )

	CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( battleSuitPowerupSound, "battlesuit.ogg" );
	CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( hastePowerupSound, "haste.ogg" );
	CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( invisibilityPowerupSound, "invisibility.ogg" );
	CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( quadDamagePowerupSound, "quad_damage.ogg" );
	CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( regenerationPowerupSound, "regeneration.ogg" );
	CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( armorRegenPowerupSound, "armor_regen.ogg" );
	CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( damagePowerupSound, "damage.ogg" );
	CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( guardPowerupSound, "guard.ogg" );
	CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE( scoutPowerupSound, "scout.ogg" );

#undef CG_REGISTER_POWERUP_ANNOUNCER_SAMPLE
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

#define CG_REGISTER_ANNOUNCER_SAMPLE(field, sample) \
	set->field = CG_RegisterRetailAnnouncerClip( profile, sample ); \
	if ( !set->field ) { \
		set->field = CG_RegisterAnnouncerClip( folder, sample ); \
	}

	CG_REGISTER_ANNOUNCER_SAMPLE( oneMinuteSound, "1_minute" );
	CG_REGISTER_ANNOUNCER_SAMPLE( fiveMinuteSound, "5_minute" );
	CG_REGISTER_ANNOUNCER_SAMPLE( suddenDeathSound, "sudden_death" );
	CG_REGISTER_ANNOUNCER_SAMPLE( overtimeSound, "overtime" );
	CG_REGISTER_ANNOUNCER_SAMPLE( oneFragSound, "1_frag" );
	CG_REGISTER_ANNOUNCER_SAMPLE( twoFragSound, "2_frags" );
	CG_REGISTER_ANNOUNCER_SAMPLE( threeFragSound, "3_frags" );

#undef CG_REGISTER_ANNOUNCER_SAMPLE
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
		cgs.media.overtimeSound = 0;
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
	CG_APPLY_ANNOUNCER_HANDLE( overtimeSound );
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
	qboolean			repairCvar;

	repairCvar = qfalse;

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
			repairCvar = qtrue;
			break;
	}

	if ( repairCvar ) {
		trap_Cvar_Set( "cg_announcer", "1" );
	}

	if ( !force && profile == cgs.announcerProfile ) {
		return;
	}

	CG_SetActiveAnnouncerProfile( profile );
	CG_RegisterPowerupAnnouncerSounds();
}

/*
=================
CG_HaveDlcGibs
=================
*/
static qboolean CG_HaveDlcGibs( void ) {
	fileHandle_t	dlcGibsFile;
	int			dlcGibsLen;

	dlcGibsLen = trap_FS_FOpenFile( "dlc_gibs/bloodspray1.tga", &dlcGibsFile, FS_READ );
	if ( dlcGibsFile ) {
		trap_FS_FCloseFile( dlcGibsFile );
	}

	return ( dlcGibsLen > 0 ) ? qtrue : qfalse;
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
	qboolean	haveDlcGibs;

	haveDlcGibs = CG_HaveDlcGibs();
	cgs.media.haveDlcGibs = haveDlcGibs;

	// voice commands
	CG_LoadVoiceChats();

	CG_RegisterAnnouncerVoiceSet( ANNOUNCER_PROFILE_DEFAULT, NULL );
	CG_RegisterAnnouncerVoiceSet( ANNOUNCER_PROFILE_VADRIGAR, "vadrigar" );
	CG_RegisterAnnouncerVoiceSet( ANNOUNCER_PROFILE_DAEMIA, "daemia" );
	CG_UpdateAnnouncerProfileFromCvar( qtrue );
#define CG_REGISTER_RETAIL_REWARD_SAMPLE(field, retailSample, fallbackSample) \
	cgs.media.field = CG_RegisterRetailAnnouncerClip( ANNOUNCER_PROFILE_DEFAULT, retailSample ); \
	if ( !cgs.media.field ) { \
		cgs.media.field = CG_RegisterAnnouncerClip( NULL, fallbackSample ); \
	}
#define CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE(field, retailSample) \
	cgs.media.field = CG_RegisterConfiguredAnnouncerClip( retailSample )
	CG_REGISTER_RETAIL_REWARD_SAMPLE( count3Sound, "three", "three" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( count2Sound, "two", "two" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( count1Sound, "one", "one" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( countFightSound, "fight", "fight" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( countPrepareSound, "prepare_to_fight", "prepare_to_fight" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( roundBeginsInSound, "round_begins_in", "round_begins_in" );
	cgs.media.raceStartBeep = CG_RegisterRaceCueSound( "start" );
	cgs.media.raceCheckpointBeep = CG_RegisterRaceCueSound( "checkpoint" );
	cgs.media.raceFinishBeep = CG_RegisterRaceCueSound( "finish" );
	cgs.media.countPrepareTeamSound = 0;

	if ( cgs.gametype >= GT_TEAM || cg_buildScript.integer ) {

		CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( countPrepareTeamSound, "prepare_your_team.ogg" );
		cgs.media.captureAwardSound = trap_S_RegisterSound( "sound/teamplay/flagcapture_yourteam.ogg", qtrue );
		CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( redLeadsSound, "red_leads.ogg" );
		CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( blueLeadsSound, "blue_leads.ogg" );
		CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( teamsTiedSound, "teams_tied.ogg" );
		cgs.media.hitTeamSound = trap_S_RegisterSound( "sound/feedback/hit_teammate.ogg", qtrue );

		CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( redScoredSound, "red_scores.ogg" );
		CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( blueScoredSound, "blue_scores.ogg" );
		CG_REGISTER_RETAIL_REWARD_SAMPLE( redWinsSound, "red_wins", "red_wins" );
		CG_REGISTER_RETAIL_REWARD_SAMPLE( blueWinsSound, "blue_wins", "blue_wins" );
		CG_REGISTER_RETAIL_REWARD_SAMPLE( redWinsRoundSound, "red_wins_round", "red_wins_round" );
		CG_REGISTER_RETAIL_REWARD_SAMPLE( blueWinsRoundSound, "blue_wins_round", "blue_wins_round" );
		CG_REGISTER_RETAIL_REWARD_SAMPLE( roundDrawSound, "round_draw", "round_draw" );
		CG_REGISTER_RETAIL_REWARD_SAMPLE( roundOverSound, "round_over", "round_over" );
		CG_REGISTER_RETAIL_REWARD_SAMPLE( lastStandingSound, "last_standing", "last_standing" );
		cgs.media.survivorWarningSound = trap_S_RegisterSound( "sound/feedback/survivor_01.ogg", qtrue );

		cgs.media.captureYourTeamSound = trap_S_RegisterSound( "sound/teamplay/flagcapture_yourteam.ogg", qtrue );
		cgs.media.captureOpponentSound = trap_S_RegisterSound( "sound/teamplay/flagcapture_opponent.ogg", qtrue );

		cgs.media.returnYourTeamSound = trap_S_RegisterSound( "sound/teamplay/flagreturn_yourteam.ogg", qtrue );
		cgs.media.returnOpponentSound = trap_S_RegisterSound( "sound/teamplay/flagreturn_opponent.ogg", qtrue );

		cgs.media.takenYourTeamSound = trap_S_RegisterSound( "sound/teamplay/flagtaken_yourteam.ogg", qtrue );
		cgs.media.takenOpponentSound = trap_S_RegisterSound( "sound/teamplay/flagtaken_opponent.ogg", qtrue );

		if ( cgs.gametype == GT_CTF || cg_buildScript.integer ) {
			CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( redFlagReturnedSound, "red_flag_returned.ogg" );
			CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( blueFlagReturnedSound, "blue_flag_returned.ogg" );
			CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( enemyTookYourFlagSound, "the_enemy_has_flag.ogg" );
			CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( yourTeamTookEnemyFlagSound, "your_team_has_flag.ogg" );
		}

		if ( cgs.gametype == GT_1FCTF || cg_buildScript.integer ) {
			// FIXME: get a replacement for this sound ?
			cgs.media.neutralFlagReturnedSound = trap_S_RegisterSound( "sound/teamplay/flagreturn_opponent.ogg", qtrue );
			CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( yourTeamTookTheFlagSound, "attack_the_flag.ogg" );
			CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( enemyTookTheFlagSound, "defend_the_flag.ogg" );
		}

		if ( cgs.gametype == GT_ATTACK_DEFEND || cg_buildScript.integer ) {
			CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( attackTheFlagSound, "attack_the_flag.ogg" );
			CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( defendTheFlagSound, "defend_the_flag.ogg" );
		}

		if ( cgs.gametype == GT_1FCTF || cgs.gametype == GT_CTF || cg_buildScript.integer ) {
			CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( youHaveFlagSound, "you_have_flag.ogg" );
			CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( holyShitSound, "holy_shit.ogg" );
		}

		if ( cgs.gametype == GT_OBELISK || cg_buildScript.integer ) {
			CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( yourBaseIsUnderAttackSound, "base_attack.ogg" );
		}

		if ( cgs.gametype == GT_DOMINATION || cg_buildScript.integer ) {
			static const char	*capturedSamples[QL_DOMINATION_ANNOUNCER_POINTS] = {
				"a_captured",
				"b_captured",
				"c_captured",
				"d_captured",
				"e_captured"
			};
			static const char	*lostSamples[QL_DOMINATION_ANNOUNCER_POINTS] = {
				"a_lost",
				"b_lost",
				"c_lost",
				"d_lost",
				"e_lost"
			};

			for ( i = 0; i < QL_DOMINATION_ANNOUNCER_POINTS; i++ ) {
				cgs.media.dominationCapturedSounds[i] = CG_RegisterRetailAnnouncerClip( ANNOUNCER_PROFILE_DEFAULT, capturedSamples[i] );
				if ( !cgs.media.dominationCapturedSounds[i] ) {
					cgs.media.dominationCapturedSounds[i] = CG_RegisterAnnouncerClip( NULL, capturedSamples[i] );
				}
				cgs.media.dominationLostSounds[i] = CG_RegisterRetailAnnouncerClip( ANNOUNCER_PROFILE_DEFAULT, lostSamples[i] );
				if ( !cgs.media.dominationLostSounds[i] ) {
					cgs.media.dominationLostSounds[i] = CG_RegisterAnnouncerClip( NULL, lostSamples[i] );
				}
			}
			cgs.media.dominationDistressSound = trap_S_RegisterSound( "sound/feedback/domination_distress.wav", qtrue );
		}
	}

	cgs.media.tracerSound = trap_S_RegisterSound( "sound/weapons/machinegun/buletby1.ogg", qfalse );
	cgs.media.selectSound = trap_S_RegisterSound( "sound/weapons/change.ogg", qfalse );
	cgs.media.wearOffSound = trap_S_RegisterSound( "sound/items/wearoff.ogg", qfalse );
	cgs.media.useNothingSound = trap_S_RegisterSound( "sound/items/use_nothing.ogg", qfalse );
	cgs.media.electroGibBounce1Sound = trap_S_RegisterSound( "sound/misc/electrogib_bounce_01.ogg", qfalse );
	cgs.media.electroGibBounce2Sound = trap_S_RegisterSound( "sound/misc/electrogib_bounce_02.ogg", qfalse );
	cgs.media.electroGibBounce3Sound = trap_S_RegisterSound( "sound/misc/electrogib_bounce_03.ogg", qfalse );
	cgs.media.electroGibBounce4Sound = trap_S_RegisterSound( "sound/misc/electrogib_bounce_04.ogg", qfalse );
	cgs.media.electroGibBounce5Sound = trap_S_RegisterSound( "sound/misc/electrogib_bounce_05.ogg", qfalse );
	if ( haveDlcGibs ) {
		cgs.media.gibSound = trap_S_RegisterSound( "dlc_gibs/gibsplt1.ogg", qfalse );
		cgs.media.gibBounce1Sound = trap_S_RegisterSound( "dlc_gibs/gibimp1.ogg", qfalse );
		cgs.media.gibBounce2Sound = trap_S_RegisterSound( "dlc_gibs/gibimp2.ogg", qfalse );
		cgs.media.gibBounce3Sound = trap_S_RegisterSound( "dlc_gibs/gibimp3.ogg", qfalse );
		cgs.media.invulnerabilityJuicedSound = trap_S_RegisterSound( "dlc_gibs/invul_juiced.ogg", qfalse );
	} else {
		cgs.media.gibSound = trap_S_RegisterSound( "sound/player/gibsplt1.wav", qfalse );
		cgs.media.gibBounce1Sound = trap_S_RegisterSound( "sound/player/gibimp1.wav", qfalse );
		cgs.media.gibBounce2Sound = trap_S_RegisterSound( "sound/player/gibimp2.wav", qfalse );
		cgs.media.gibBounce3Sound = trap_S_RegisterSound( "sound/player/gibimp3.wav", qfalse );
		cgs.media.invulnerabilityJuicedSound = 0;
	}

	cgs.media.useInvulnerabilitySound = trap_S_RegisterSound( "sound/items/invul_activate.ogg", qfalse );
	cgs.media.invulnerabilityImpactSound1 = trap_S_RegisterSound( "sound/items/invul_impact_01.ogg", qfalse );
	cgs.media.invulnerabilityImpactSound2 = trap_S_RegisterSound( "sound/items/invul_impact_02.ogg", qfalse );
	cgs.media.invulnerabilityImpactSound3 = trap_S_RegisterSound( "sound/items/invul_impact_03.ogg", qfalse );
	cgs.media.obeliskHitSound1 = trap_S_RegisterSound( "sound/items/obelisk_hit_01.ogg", qfalse );
	cgs.media.obeliskHitSound2 = trap_S_RegisterSound( "sound/items/obelisk_hit_02.ogg", qfalse );
	cgs.media.obeliskHitSound3 = trap_S_RegisterSound( "sound/items/obelisk_hit_03.ogg", qfalse );
	cgs.media.obeliskRespawnSound = trap_S_RegisterSound( "sound/items/obelisk_respawn.ogg", qfalse );

	cgs.media.ammoregenSound = trap_S_RegisterSound("sound/items/cl_ammoregen.wav", qfalse);
	cgs.media.armorregenSound = trap_S_RegisterSound("sound/misc/ar1_pkup.ogg", qfalse);
	cgs.media.doublerSound = trap_S_RegisterSound("sound/items/cl_doubler.wav", qfalse);
	cgs.media.guardSound = trap_S_RegisterSound("sound/items/cl_guard.wav", qfalse);
	cgs.media.scoutSound = trap_S_RegisterSound("sound/items/cl_scout.wav", qfalse);

	cgs.media.teleInSound = trap_S_RegisterSound( "sound/world/telein.ogg", qfalse );
	cgs.media.teleOutSound = trap_S_RegisterSound( "sound/world/teleout.ogg", qfalse );
	cgs.media.lowAmmoSound = trap_S_RegisterSound( "sound/weapons/lowammo.ogg", qfalse );
	cgs.media.respawnSound = trap_S_RegisterSound( "sound/items/respawn1.ogg", qfalse );
	cgs.media.thawTickSound = trap_S_RegisterSound( "sound/misc/tim_pump.ogg", qfalse );

	cgs.media.noAmmoSound = trap_S_RegisterSound( "sound/weapons/noammo.ogg", qfalse );

	cgs.media.talkSound = trap_S_RegisterSound( "sound/player/talk.ogg", qfalse );
	cgs.media.landSound = trap_S_RegisterSound( "sound/player/land1.ogg", qfalse);

	cgs.media.hitSound = trap_S_RegisterSound( "sound/feedback/hit.wav", qfalse );
	cgs.media.hitSoundHighArmor = trap_S_RegisterSound( "sound/feedback/hithi.wav", qfalse );
	cgs.media.hitSoundLowArmor = trap_S_RegisterSound( "sound/feedback/hitlo.wav", qfalse );

	cgs.media.impressiveSound = trap_S_RegisterSound( "sound/feedback/impressive.wav", qtrue );
	cgs.media.impressiveSound2 = trap_S_RegisterSound( "sound/feedback/impressive2.wav", qtrue );
	cgs.media.impressiveSound3 = trap_S_RegisterSound( "sound/feedback/impressive3.wav", qtrue );
	cgs.media.excellentSound = trap_S_RegisterSound( "sound/feedback/excellent.wav", qtrue );
	cgs.media.deniedSound = trap_S_RegisterSound( "sound/feedback/denied.wav", qtrue );
	cgs.media.humiliationSound = trap_S_RegisterSound( "sound/feedback/humiliation.wav", qtrue );
	cgs.media.assistSound = trap_S_RegisterSound( "sound/feedback/assist.wav", qtrue );
	cgs.media.defendSound = trap_S_RegisterSound( "sound/feedback/defense.wav", qtrue );
	cgs.media.firstImpressiveSound = trap_S_RegisterSound( "sound/feedback/first_impressive.wav", qtrue );
	cgs.media.firstExcellentSound = trap_S_RegisterSound( "sound/feedback/first_excellent.wav", qtrue );
	cgs.media.firstHumiliationSound = trap_S_RegisterSound( "sound/feedback/first_gauntlet.wav", qtrue );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( comboKillSound, "combokill1", "combokill1" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( comboKillSound2, "combokill2", "combokill2" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( comboKillSound3, "combokill3", "combokill3" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( midairSound, "midair1", "midair1" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( midairSound2, "midair2", "midair2" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( midairSound3, "midair3", "midair3" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( accuracySound, "accuracy", "accuracy" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( perfectSound, "perfect", "perfect" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( quadGodSound, "quad_god", "quad_god" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( rampageSound, "rampage1", "rampage" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( rampageSound2, "rampage2", "rampage" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( rampageSound3, "rampage3", "rampage" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( revengeSound, "revenge1", "revenge" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( revengeSound2, "revenge2", "revenge" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( revengeSound3, "revenge3", "revenge" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( perforatedSound, "perforated", "perforated" );
	if ( cgs.gametype == GT_RED_ROVER || cg_buildScript.integer ) {
		CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( biteSound, "bite.ogg" );
		cgs.media.kamikazeRespawnSound = trap_S_RegisterSound( "sound/items/kamikazerespawn.wav", qfalse );
	}
	CG_REGISTER_RETAIL_REWARD_SAMPLE( headshotSound, "headshot", "headshot" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( firstFragSound, "first_frag", "first_frag" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( infectedSound, "infected", "infected" );
	CG_REGISTER_RETAIL_REWARD_SAMPLE( newHighScoreSound, "new_high_score", "new_high_score" );

	CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( takenLeadSound, "lead_taken.ogg" );
	CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( tiedLeadSound, "lead_tied.ogg" );
	CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( lostLeadSound, "lead_lost.ogg" );

	CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( voteNow, "vote_now.ogg" );
	CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( votePassed, "vote_passed.ogg" );
	CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE( voteFailed, "vote_failed.ogg" );

#undef CG_REGISTER_CONFIGURED_ANNOUNCER_SAMPLE
#undef CG_REGISTER_RETAIL_REWARD_SAMPLE

	cgs.media.watrInSound = trap_S_RegisterSound( "sound/player/watr_in.ogg", qfalse);
	cgs.media.watrOutSound = trap_S_RegisterSound( "sound/player/watr_out.ogg", qfalse);
	cgs.media.watrUnSound = trap_S_RegisterSound( "sound/player/watr_un.ogg", qfalse);

	cgs.media.jumpPadSound = trap_S_RegisterSound ("sound/world/jumppad.ogg", qfalse );

	for (i=0 ; i<4 ; i++) {
		Com_sprintf (name, sizeof(name), "sound/player/footsteps/step%i.ogg", i+1);
		cgs.media.footsteps[FOOTSTEP_NORMAL][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/boot%i.ogg", i+1);
		cgs.media.footsteps[FOOTSTEP_BOOT][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/flesh%i.ogg", i+1);
		cgs.media.footsteps[FOOTSTEP_FLESH][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/mech%i.ogg", i+1);
		cgs.media.footsteps[FOOTSTEP_MECH][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/energy%i.ogg", i+1);
		cgs.media.footsteps[FOOTSTEP_ENERGY][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/splash%i.ogg", i+1);
		cgs.media.footsteps[FOOTSTEP_SPLASH][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/clank%i.ogg", i+1);
		cgs.media.footsteps[FOOTSTEP_METAL][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/snow%i.ogg", i+1);
		cgs.media.footsteps[FOOTSTEP_SNOW][i] = trap_S_RegisterSound (name, qfalse);

		Com_sprintf (name, sizeof(name), "sound/player/footsteps/wood%i.ogg", i+1);
		cgs.media.footsteps[FOOTSTEP_WOOD][i] = trap_S_RegisterSound (name, qfalse);
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
	cgs.media.flightSound = trap_S_RegisterSound( "sound/items/flight.ogg", qfalse );
	cgs.media.medkitSound = trap_S_RegisterSound ("sound/items/use_medkit.ogg", qfalse);
	cgs.media.quadSound = trap_S_RegisterSound("sound/items/damage3.ogg", qfalse);
	cgs.media.sfx_ric1 = trap_S_RegisterSound( "sound/weapons/machinegun/ric1.ogg", qfalse );
	cgs.media.sfx_ric2 = trap_S_RegisterSound( "sound/weapons/machinegun/ric2.ogg", qfalse );
	cgs.media.sfx_ric3 = trap_S_RegisterSound( "sound/weapons/machinegun/ric3.ogg", qfalse );
	cgs.media.sfx_railg = trap_S_RegisterSound( "sound/weapons/railgun/railgf1a.ogg", qfalse );
	cgs.media.sfx_rockexp = trap_S_RegisterSound( "sound/weapons/rocket/rocklx1a.ogg", qfalse );
	cgs.media.sfx_plasmaexp = trap_S_RegisterSound( "sound/weapons/plasma/plasmx1a.ogg", qfalse );
	cgs.media.sfx_proxexp = trap_S_RegisterSound( "sound/weapons/proxmine/wstbexpl.ogg", qfalse );
	cgs.media.sfx_nghit = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpd.ogg", qfalse );
	cgs.media.sfx_nghitflesh = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpl.ogg", qfalse );
	cgs.media.sfx_nghitmetal = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpm.ogg", qfalse );
	cgs.media.sfx_chghit = trap_S_RegisterSound( "sound/weapons/vulcan/wvulimpd.ogg", qfalse );
	cgs.media.sfx_chghitflesh = trap_S_RegisterSound( "sound/weapons/vulcan/wvulimpl.ogg", qfalse );
	cgs.media.sfx_chghitmetal = trap_S_RegisterSound( "sound/weapons/vulcan/wvulimpm.ogg", qfalse );
	cgs.media.sfx_chgwind = trap_S_RegisterSound( "sound/weapons/vulcan/wvulwind.ogg", qfalse );
	cgs.media.weaponHoverSound = trap_S_RegisterSound( "sound/weapons/weapon_hover.ogg", qfalse );
	cgs.media.kamikazeExplodeSound = trap_S_RegisterSound( "sound/items/kam_explode.ogg", qfalse );
	cgs.media.kamikazeImplodeSound = trap_S_RegisterSound( "sound/items/kam_implode.ogg", qfalse );
	cgs.media.kamikazeFarSound = trap_S_RegisterSound( "sound/items/kam_explode_far.ogg", qfalse );
	cgs.media.winnerSound = CG_RegisterConfiguredAnnouncerClip( "you_win.ogg" );
	cgs.media.loserSound = CG_RegisterConfiguredAnnouncerClip( "you_lose.ogg" );
	cgs.media.youSuckSound = trap_S_RegisterSound( "sound/misc/yousuck.ogg", qfalse );

	cgs.media.wstbimplSound = trap_S_RegisterSound( "sound/weapons/proxmine/wstbimpl.ogg", qfalse );
	cgs.media.wstbimpmSound = trap_S_RegisterSound( "sound/weapons/proxmine/wstbimpm.ogg", qfalse );
	cgs.media.wstbimpdSound = trap_S_RegisterSound( "sound/weapons/proxmine/wstbimpd.ogg", qfalse );
	cgs.media.wstbactvSound = trap_S_RegisterSound( "sound/weapons/proxmine/wstbactv.ogg", qfalse );

	cgs.media.regenSound = trap_S_RegisterSound("sound/items/regen.ogg", qfalse);
	cgs.media.protectSound = trap_S_RegisterSound("sound/items/protect3.ogg", qfalse);
	cgs.media.n_healthSound = trap_S_RegisterSound("sound/items/n_health.ogg", qfalse );
	cgs.media.hgrenb1aSound = trap_S_RegisterSound("sound/weapons/grenade/hgrenb1a.ogg", qfalse);
	cgs.media.hgrenb2aSound = trap_S_RegisterSound("sound/weapons/grenade/hgrenb2a.ogg", qfalse);

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
CG_ShouldRegisterPOIPowerupShaders

Matches the retail gametype gate around the projected item/teammate POI
powerup icon bank, while preserving build-script asset discovery.
=================
*/
static qboolean CG_ShouldRegisterPOIPowerupShaders( void ) {
	if ( cg_buildScript.integer ) {
		return qtrue;
	}

	switch ( cgs.gametype ) {
	case GT_RACE:
	case GT_CLAN_ARENA:
	case GT_DOMINATION:
	case GT_RED_ROVER:
		return qfalse;
	default:
		return qtrue;
	}
}

/*
=================
CG_ShouldRegisterFlagStatusShaders

Matches the retail objective-gametype gate around the flag-status icon bank
for the dropped-marker subset currently exposed through cgs.media.
=================
*/
static qboolean CG_ShouldRegisterFlagStatusShaders( void ) {
	if ( cg_buildScript.integer ) {
		return qtrue;
	}

	switch ( cgs.gametype ) {
	case GT_RACE:
	case GT_CTF:
	case GT_1FCTF:
	case GT_OBELISK:
	case GT_DOMINATION:
	case GT_ATTACK_DEFEND:
		return qtrue;
	default:
		return qfalse;
	}
}

/*
=================
CG_RegisterGraphics

This function may execute for a couple of minutes with a slow disk.
=================
*/
static void CG_RegisterGraphics( void ) {
	int			i;
	char		items[MAX_ITEMS+1];
	qboolean		haveDlcGibs;
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
	haveDlcGibs = CG_HaveDlcGibs();
	cgs.media.haveDlcGibs = haveDlcGibs;

	// clear any references to old media
	memset( &cg.refdef, 0, sizeof( cg.refdef ) );
	trap_R_ClearScene();

	CG_LoadingString( CG_ConfigString( CS_MESSAGE ) );

	trap_R_LoadWorldMap( cgs.mapname );

	// precache status bar pics
	CG_LoadingString( "game media" );

	for ( i=0 ; i<11 ; i++) {
		cgs.media.numberShaders[i] = trap_R_RegisterShader( sb_nums[i] );
	}

	cgs.media.healthSegmentShader = trap_R_RegisterShader( "gfx/2d/health_segment.tga" );

	cgs.media.botSkillShaders[0] = trap_R_RegisterShader( "menu/art/skill1.tga" );
	cgs.media.botSkillShaders[1] = trap_R_RegisterShader( "menu/art/skill2.tga" );
	cgs.media.botSkillShaders[2] = trap_R_RegisterShader( "menu/art/skill3.tga" );
	cgs.media.botSkillShaders[3] = trap_R_RegisterShader( "menu/art/skill4.tga" );
	cgs.media.botSkillShaders[4] = trap_R_RegisterShader( "menu/art/skill5.tga" );

	cgs.media.viewDamageBlendShader = trap_R_RegisterShader( "viewDamageBlend" );
	if ( haveDlcGibs ) {
		cgs.media.viewBloodShader = trap_R_RegisterShader( "viewBloodBlend" );
	} else {
		cgs.media.viewBloodShader = 0;
	}

	cgs.media.deferShader = trap_R_RegisterShaderNoMip( "gfx/2d/defer.tga" );

	cgs.media.scoreboardName = trap_R_RegisterShaderNoMip( "menu/tab/name.tga" );
	cgs.media.scoreboardPing = trap_R_RegisterShaderNoMip( "menu/tab/ping.tga" );
	cgs.media.scoreboardScore = trap_R_RegisterShaderNoMip( "menu/tab/score.tga" );
	cgs.media.scoreboardTime = trap_R_RegisterShaderNoMip( "menu/tab/time.tga" );
	cgs.media.scoreboxSpecShader = trap_R_RegisterShaderNoMip( "ui/assets/score/scorebox_spec.tga" );
	cgs.media.scoreboxFollowShader = trap_R_RegisterShaderNoMip( "ui/assets/score/scorebox_follow.tga" );
	if ( cgs.gametype == GT_TOURNAMENT || cg_buildScript.integer ) {
		cgs.media.scoreFirstPlayerReadyShader = trap_R_RegisterShaderNoMip( "ui/assets/score/1st_plyr_ready.tga" );
		cgs.media.scoreFirstPlayerNotReadyShader = trap_R_RegisterShaderNoMip( "ui/assets/score/1st_plyr_notready.tga" );
		cgs.media.scoreSecondPlayerReadyShader = trap_R_RegisterShaderNoMip( "ui/assets/score/2nd_plyr_ready.tga" );
		cgs.media.scoreSecondPlayerNotReadyShader = trap_R_RegisterShaderNoMip( "ui/assets/score/2nd_plyr_notready.tga" );
		cgs.media.scoreFirstPlayerLeadsShader = trap_R_RegisterShaderNoMip( "ui/assets/score/1st_plyr_leads.tga" );
		cgs.media.scoreFirstPlayerTiedShader = trap_R_RegisterShaderNoMip( "ui/assets/score/1st_plyr_tied.tga" );
		cgs.media.scoreFirstPlayerTrailsShader = trap_R_RegisterShaderNoMip( "ui/assets/score/1st_plyr_trails.tga" );
		cgs.media.scoreSecondPlayerLeadsShader = trap_R_RegisterShaderNoMip( "ui/assets/score/2nd_plyr_leads.tga" );
		cgs.media.scoreSecondPlayerTiedShader = trap_R_RegisterShaderNoMip( "ui/assets/score/2nd_plyr_tied.tga" );
		cgs.media.scoreSecondPlayerTrailsShader = trap_R_RegisterShaderNoMip( "ui/assets/score/2nd_plyr_trails.tga" );
	}
	cgs.media.scoreArrowGreenShader = trap_R_RegisterShader( "ui/assets/score/arrowg.tga" );
	cgs.media.scoreArrowRedShader = trap_R_RegisterShader( "ui/assets/score/arrowr.tga" );
	if ( cgs.gametype >= GT_TEAM || cg_buildScript.integer ) {
		cgs.media.scoreCAArrowRedShader = trap_R_RegisterShader( "ui/assets/score/ca_arrow_red.tga" );
		cgs.media.scoreCAArrowBlueShader = trap_R_RegisterShader( "ui/assets/score/ca_arrow_blue.tga" );
	}
	cgs.media.scoreMutedShader = trap_R_RegisterShaderNoMip( "ui/assets/score/muted" );
	cgs.media.scoreSpeakingShader = trap_R_RegisterShaderNoMip( "ui/assets/score/speaking" );
	cgs.media.inkFadeLeftShader = trap_R_RegisterShaderNoMip( "ui/assets/score/ink_fade_left.tga" );
	cgs.media.inkFadeRightShader = trap_R_RegisterShaderNoMip( "ui/assets/score/ink_fade_right.tga" );

	cgs.media.smokePuffShader = trap_R_RegisterShader( "smokePuff" );
	cgs.media.surfacePuffShader = trap_R_RegisterShader( "surfacePuff" );
	cgs.media.smokePuffRageProShader = trap_R_RegisterShader( "smokePuffRagePro" );
	cgs.media.shotgunSmokePuffShader = trap_R_RegisterShader( "shotgunSmokePuff" );
	cgs.media.nailPuffShader = trap_R_RegisterShader( "nailtrail" );
	cgs.media.blueProxMine = trap_R_RegisterModel( "models/weaphits/proxmineb.md3" );
	cgs.media.plasmaBallShader = trap_R_RegisterShader( "sprites/plasma1" );
	cgs.media.bloodTrailShader = trap_R_RegisterShader( "bloodTrail" );
	if ( haveDlcGibs ) {
		cgs.media.bloodSprayShaders[0] = trap_R_RegisterShader( "bloodSpray1" );
		cgs.media.bloodSprayShaders[1] = trap_R_RegisterShader( "bloodSpray2" );
		cgs.media.bloodSprayShaders[2] = trap_R_RegisterShader( "bloodSpray3" );
		cgs.media.bloodSprayShaders[3] = trap_R_RegisterShader( "bloodSpray4" );
	} else {
		cgs.media.bloodSprayShaders[0] = 0;
		cgs.media.bloodSprayShaders[1] = 0;
		cgs.media.bloodSprayShaders[2] = 0;
		cgs.media.bloodSprayShaders[3] = 0;
	}
	cgs.media.lagometerShader = trap_R_RegisterShader("lagometer" );
	cgs.media.connectionShader = trap_R_RegisterShader( "disconnected" );

	cgs.media.waterBubbleShader = trap_R_RegisterShader( "waterBubble" );

	cgs.media.vignetteShader = trap_R_RegisterShader( "gfx/misc/vignette" );
	cgs.media.tracerShader = trap_R_RegisterShader( "gfx/misc/tracer" );
	cgs.media.iceTrailShader = trap_R_RegisterShader( "iceTrail" );
	cgs.media.iceballShader = trap_R_RegisterShader( "gfx/misc/iceball" );
	cgs.media.selectShader = trap_R_RegisterShader( "gfx/2d/select" );
	cgs.media.weaponBarLitShader = trap_R_RegisterShader( "ui/assets/hud/weaplit2.tga" );
	cgs.media.weaponBarIdle1Shader = trap_R_RegisterShader( "ui/assets/hud/weapidle1.tga" );
	cgs.media.weaponBarIdle2Shader = trap_R_RegisterShader( "ui/assets/hud/weapidle2.tga" );

	for ( i = 1 ; i < NUM_CROSSHAIRS ; i++ ) {
		cgs.media.crosshairShader[i] = trap_R_RegisterShader( va( "gfx/2d/crosshair%d", i ) );
	}

	cgs.media.backTileShader = trap_R_RegisterShader( "gfx/2d/backtile" );
	cgs.media.noammoShader = trap_R_RegisterShader( "icons/noammo" );
	cgs.media.infiniteAmmoShader = trap_R_RegisterShader( "icons/infinite.tga" );
	cgs.media.healthBar200 = trap_R_RegisterShaderNoMip( "ui/assets/hud/h200.tga" );
	cgs.media.healthBar100 = trap_R_RegisterShaderNoMip( "ui/assets/hud/h100.tga" );
	cgs.media.armorBar200 = trap_R_RegisterShaderNoMip( "ui/assets/hud/a200.tga" );
	cgs.media.armorBar100 = trap_R_RegisterShaderNoMip( "ui/assets/hud/a100.tga" );
	cgs.media.healthTick200 = trap_R_RegisterShaderNoMip( "ui/assets/hud/h200line.tga" );
	cgs.media.healthTick100 = trap_R_RegisterShaderNoMip( "ui/assets/hud/h100line.tga" );
	cgs.media.armorTick200 = trap_R_RegisterShaderNoMip( "ui/assets/hud/a200line.tga" );
	cgs.media.armorTick100 = trap_R_RegisterShaderNoMip( "ui/assets/hud/a100line.tga" );
	CG_RegisterGameTypeIcons();

	// powerup shaders
	cgs.media.quadShader = trap_R_RegisterShader("powerups/quad" );
	cgs.media.quadWeaponShader = trap_R_RegisterShader("powerups/quadWeapon" );
	cgs.media.battleSuitShader = trap_R_RegisterShader("powerups/battleSuit" );
	cgs.media.battleWeaponShader = trap_R_RegisterShader("powerups/battleWeapon" );
	cgs.media.invisShader = trap_R_RegisterShader("powerups/invisibility" );
	cgs.media.ghostWeaponShader = trap_R_RegisterShader("ghostWeaponShader" );
	cgs.media.regenShader = trap_R_RegisterShader("powerups/regen" );
	cgs.media.hastePuffShader = trap_R_RegisterShader("hasteSmokePuff" );
	if ( CG_ShouldRegisterPOIPowerupShaders() ) {
		cgs.media.poiPowerupQuadShader = trap_R_RegisterShader( "gfx/2d/powerup/quad" );
		cgs.media.poiPowerupBattleSuitShader = trap_R_RegisterShader( "gfx/2d/powerup/bs" );
		cgs.media.poiPowerupHasteShader = trap_R_RegisterShader( "gfx/2d/powerup/haste" );
		cgs.media.poiPowerupInvisShader = trap_R_RegisterShader( "gfx/2d/powerup/invis" );
		cgs.media.poiPowerupRegenShader = trap_R_RegisterShader( "gfx/2d/powerup/regen" );
		cgs.media.poiPowerupIncomingShader = trap_R_RegisterShader( "gfx/2d/powerup/incoming" );
	}
	if ( CG_ShouldRegisterFlagStatusShaders() ) {
		cgs.media.poiFlagDroppedNeutralShader = trap_R_RegisterShader( "gfx/2d/flag_status/flag_dropped" );
		cgs.media.poiFlagDroppedRedShader = trap_R_RegisterShader( "gfx/2d/flag_status/red_flag_dropped" );
		cgs.media.poiFlagDroppedBlueShader = trap_R_RegisterShader( "gfx/2d/flag_status/blue_flag_dropped" );
	}
	if ( cgs.gametype == GT_FFA || cg_buildScript.integer ) {
		cgs.media.poiQuadHogShader = trap_R_RegisterShader( "gfx/2d/quad_hog/quadhog" );
	}
	if ( cgs.gametype == GT_RED_ROVER || cg_buildScript.integer ) {
		cgs.media.poiInfectedShader = trap_R_RegisterShader( "gfx/2d/infected/bite" );
	}
	cgs.media.poiUnavailableShader = trap_R_RegisterShader( "gfx/2d/unavailable" );
	cgs.media.itemTimerArmorShader = trap_R_RegisterShader( "gfx/2d/timer/armor" );
	cgs.media.itemTimerBattleSuitShader = trap_R_RegisterShader( "gfx/2d/timer/bs" );
	cgs.media.itemTimerHasteShader = trap_R_RegisterShader( "gfx/2d/timer/haste" );
	cgs.media.itemTimerHealthShader = trap_R_RegisterShader( "gfx/2d/timer/health" );
	cgs.media.itemTimerInvisShader = trap_R_RegisterShader( "gfx/2d/timer/invis" );
	cgs.media.itemTimerMedkitShader = trap_R_RegisterShader( "gfx/2d/timer/medkit" );
	cgs.media.itemTimerQuadShader = trap_R_RegisterShader( "gfx/2d/timer/quad" );
	cgs.media.itemTimerRegenShader = trap_R_RegisterShader( "gfx/2d/timer/regen" );
	cgs.media.itemTimerUnknownShader = trap_R_RegisterShader( "gfx/2d/timer/unknown" );
	cgs.media.itemTimerSlice5Shader = trap_R_RegisterShader( "gfx/2d/timer/slice5" );
	cgs.media.itemTimerSlice5CurrentShader = trap_R_RegisterShader( "gfx/2d/timer/slice5_current" );
	cgs.media.itemTimerSlice7Shader = trap_R_RegisterShader( "gfx/2d/timer/slice7" );
	cgs.media.itemTimerSlice7CurrentShader = trap_R_RegisterShader( "gfx/2d/timer/slice7_current" );
	cgs.media.itemTimerSlice12Shader = trap_R_RegisterShader( "gfx/2d/timer/slice12" );
	cgs.media.itemTimerSlice12CurrentShader = trap_R_RegisterShader( "gfx/2d/timer/slice12_current" );
	cgs.media.itemTimerSlice24Shader = trap_R_RegisterShader( "gfx/2d/timer/slice24" );
	cgs.media.itemTimerSlice24CurrentShader = trap_R_RegisterShader( "gfx/2d/timer/slice24_current" );

	if ( cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF || cgs.gametype == GT_HARVESTER || cg_buildScript.integer ) {
		cgs.media.redCubeModel = trap_R_RegisterModel( "models/powerups/orb/r_orb.md3" );
		cgs.media.blueCubeModel = trap_R_RegisterModel( "models/powerups/orb/b_orb.md3" );
		cgs.media.redCubeIcon = trap_R_RegisterShader( "icons/skull_red" );
		cgs.media.blueCubeIcon = trap_R_RegisterShader( "icons/skull_blue" );
		if ( cgs.gametype == GT_HARVESTER || cg_buildScript.integer ) {
			cgs.media.poiHarvesterCaptureShader = trap_R_RegisterShader( "gfx/2d/har/poi_capture" );
		}
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
		cgs.media.friendShader = trap_R_RegisterShader( "sprites/friend" );
		cgs.media.friendHitShader = trap_R_RegisterShader( "sprites/friend_hit" );
		cgs.media.friendDeadShader = trap_R_RegisterShader( "sprites/friend_dead" );
		cgs.media.frozenPlayerShader = trap_R_RegisterShader( "sprites/frozen" );
		cgs.media.redQuadShader = trap_R_RegisterShader("powerups/blueflag" );
		cgs.media.teamStatusBar = trap_R_RegisterShader( "gfx/2d/colorbar" );
		cgs.media.blueKamikazeShader = trap_R_RegisterShader( "models/weaphits/kamikblu" );
	}

	if ( cgs.gametype == GT_CTF || cgs.gametype == GT_1FCTF || cgs.gametype == GT_ATTACK_DEFEND || cg_buildScript.integer ) {
		cgs.media.flagCarrierShader = trap_R_RegisterShader( "sprites/flagcarrier" );
		cgs.media.flagCarrierHitShader = trap_R_RegisterShader( "sprites/flagcarrier_hit" );
		cgs.media.poiNeutralFlagCarrierShader = trap_R_RegisterShader( "sprites/neutralflagcarrier" );
	}

	cgs.media.poiAttackShader = trap_R_RegisterShader( "gfx/2d/ad/poi_attack" );
	cgs.media.poiCaptureShader = trap_R_RegisterShader( "gfx/2d/ad/poi_capture" );
	cgs.media.poiDefendShader = trap_R_RegisterShader( "gfx/2d/ad/poi_defend" );

	cgs.media.armorModel = trap_R_RegisterModel( "models/powerups/armor/armor_yel.md3" );
	cgs.media.armorIcon  = trap_R_RegisterShaderNoMip( "icons/iconr_yellow" );

	cgs.media.machinegunBrassModel = trap_R_RegisterModel( "models/weapons2/shells/m_shell.md3" );
	cgs.media.shotgunBrassModel = trap_R_RegisterModel( "models/weapons2/shells/s_shell.md3" );

	if ( haveDlcGibs ) {
		cgs.media.gibAbdomen = trap_R_RegisterModel( "dlc_gibs/abdomen.md3" );
		cgs.media.gibArm = trap_R_RegisterModel( "dlc_gibs/arm.md3" );
		cgs.media.gibChest = trap_R_RegisterModel( "dlc_gibs/chest.md3" );
		cgs.media.gibFist = trap_R_RegisterModel( "dlc_gibs/fist.md3" );
		cgs.media.gibFoot = trap_R_RegisterModel( "dlc_gibs/foot.md3" );
		cgs.media.gibForearm = trap_R_RegisterModel( "dlc_gibs/forearm.md3" );
		cgs.media.gibIntestine = trap_R_RegisterModel( "dlc_gibs/intestine.md3" );
		cgs.media.gibLeg = trap_R_RegisterModel( "dlc_gibs/leg.md3" );
		cgs.media.gibSkull = trap_R_RegisterModel( "dlc_gibs/skull.md3" );
		cgs.media.gibBrain = trap_R_RegisterModel( "dlc_gibs/brain.md3" );
	} else {
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
	}
	cg_gibSphereModel = trap_R_RegisterModel( "models/gibs/sphere.md3" );

	cgs.media.smoke2 = trap_R_RegisterModel( "models/weapons2/shells/s_shell.md3" );

	cgs.media.balloonShader = trap_R_RegisterShader( "sprites/balloon3" );

	cgs.media.bloodExplosionShader = trap_R_RegisterShader( "bloodExplosion" );
	cg_deathEffectShader = trap_R_RegisterShader( "deathEffect" );

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
	if ( haveDlcGibs ) {
		cgs.media.invulnerabilityJuicedModel = trap_R_RegisterModel( "dlc_gibs/juicer.md3" );
	} else {
		cgs.media.invulnerabilityJuicedModel = trap_R_RegisterModel( "models/powerups/shield/juicer.md3" );
	}
	cgs.media.medkitUsageModel = trap_R_RegisterModel( "models/powerups/regen.md3" );
	cgs.media.heartShader = trap_R_RegisterShaderNoMip( "ui/assets/statusbar/selectedhealth.tga" );


	cgs.media.invulnerabilityPowerupModel = trap_R_RegisterModel( "models/powerups/shield/shield.md3" );
	cgs.media.medalImpressive = trap_R_RegisterShaderNoMip( "medal_impressive" );
	cgs.media.medalExcellent = trap_R_RegisterShaderNoMip( "medal_excellent" );
	cgs.media.medalGauntlet = trap_R_RegisterShaderNoMip( "medal_gauntlet" );
	cgs.media.medalDefend = trap_R_RegisterShaderNoMip( "medal_defense" );
	cgs.media.medalAssist = trap_R_RegisterShaderNoMip( "medal_assist" );
	cgs.media.medalCapture = trap_R_RegisterShaderNoMip( "medal_capture" );
	cgs.media.medalAccuracy = trap_R_RegisterShaderNoMip( "medal_accuracy" );
	cgs.media.medalComboKill = trap_R_RegisterShaderNoMip( "medal_combokill" );
	cgs.media.medalMidair = trap_R_RegisterShaderNoMip( "medal_midair" );
	cgs.media.medalPerfect = trap_R_RegisterShaderNoMip( "medal_perfect" );
	cgs.media.medalPerforated = trap_R_RegisterShaderNoMip( "medal_perforated" );
	cgs.media.medalQuadGod = trap_R_RegisterShaderNoMip( "medal_quadgod" );
	cgs.media.medalRampage = trap_R_RegisterShaderNoMip( "medal_rampage" );
	cgs.media.medalRevenge = trap_R_RegisterShaderNoMip( "medal_revenge" );
	cgs.media.medalHeadshot = trap_R_RegisterShaderNoMip( "medal_headshot" );
	cgs.media.medalFirstFrag = trap_R_RegisterShaderNoMip( "medal_firstfrag" );


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
	cgs.media.iceMarkShader = trap_R_RegisterShader( "iceMark" );
	cgs.media.holeMarkShader = trap_R_RegisterShader( "gfx/damage/hole_lg_mrk" );
	cgs.media.energyMarkShader = trap_R_RegisterShader( "gfx/damage/plasma_mrk" );
	cgs.media.shadowMarkShader = trap_R_RegisterShader( "markShadow" );
	cgs.media.wakeMarkShader = trap_R_RegisterShader( "wake" );
	cgs.media.bloodMarkShader = trap_R_RegisterShader( "bloodMark" );

	cgs.media.waterIcon = trap_R_RegisterShader( "gfx/hud/icons/water" );
	cgs.media.slimeIcon = trap_R_RegisterShader( "gfx/hud/icons/slime" );
	cgs.media.lavaIcon = trap_R_RegisterShader( "gfx/hud/icons/lava" );
	cgs.media.crushIcon = trap_R_RegisterShader( "gfx/hud/icons/crush" );
	cgs.media.telefragIcon = trap_R_RegisterShader( "gfx/hud/icons/telefrag" );
	cgs.media.fallingIcon = trap_R_RegisterShader( "gfx/hud/icons/falling" );
	cgs.media.suicideIcon = trap_R_RegisterShader( "gfx/hud/icons/skull" );
	cgs.media.kamikazeIcon = trap_R_RegisterShader( "gfx/hud/icons/kamikaze" );
	cgs.media.juicedIcon = trap_R_RegisterShader( "gfx/hud/icons/juiced" );

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
	cgs.media.selectCursor = trap_R_RegisterShaderNoMip( "ui/assets/3_cursor3.tga" );
	cgs.media.raceNavShader = trap_R_RegisterShader( "gfx/misc/racenav.jpg" );
	cgs.media.raceStartShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/start" );
	cgs.media.raceCheckpointShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/checkpoint" );
	cgs.media.raceFinishShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/finish" );
	cgs.media.raceCommandUpShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_up" );
	cgs.media.raceCommandDownShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_down" );
	cgs.media.raceCommandRightShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_right" );
	cgs.media.raceCommandLeftShader = trap_R_RegisterShaderNoMip( "gfx/2d/race/cmd_left" );

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
CG_CompareSpectatorClients

=======================
*/
static int QDECL CG_CompareSpectatorClients( const void *a, const void *b ) {
	const clientInfo_t	*clientA;
	const clientInfo_t	*clientB;
	int			clientNumA;
	int			clientNumB;

	clientNumA = *(const int *)a;
	clientNumB = *(const int *)b;
	clientA = &cgs.clientinfo[clientNumA];
	clientB = &cgs.clientinfo[clientNumB];

	if ( clientA->spectateOnly > clientB->spectateOnly ) {
		return 1;
	}
	if ( clientA->spectateOnly < clientB->spectateOnly ) {
		return -1;
	}

	if ( clientA->spectatorQueuePosition > clientB->spectatorQueuePosition ) {
		return 1;
	}
	if ( clientA->spectatorQueuePosition < clientB->spectatorQueuePosition ) {
		return -1;
	}

	return clientNumA - clientNumB;
}

/*																																			
=======================
CG_BuildSpectatorString

=======================
*/
void CG_BuildSpectatorString() {
	int		i;
	int		newEntryCount;
	int		spectatorClients[MAX_CLIENTS];
	char		newSpectatorList[MAX_STRING_CHARS];
	char		newSpectatorEntries[MAX_CLIENTS][64];
	qboolean	cacheChanged;

	newSpectatorList[0] = '\0';
	memset( newSpectatorEntries, 0, sizeof( newSpectatorEntries ) );
	newEntryCount = 0;

	for ( i = 0; i < MAX_CLIENTS; i++ ) {
		const clientInfo_t	*ci;

		ci = &cgs.clientinfo[i];
		if ( !ci->infoValid || ci->team != TEAM_SPECTATOR ) {
			continue;
		}

		spectatorClients[newEntryCount] = i;
		newEntryCount++;
		Q_strcat( newSpectatorList, sizeof( newSpectatorList ), va( "%s     ", ci->name ) );
	}

	if ( newEntryCount > 1 ) {
		qsort( spectatorClients, newEntryCount, sizeof( spectatorClients[0] ), CG_CompareSpectatorClients );
	}

	for ( i = 0; i < newEntryCount; i++ ) {
		const clientInfo_t	*ci;
		char			cleanName[MAX_NAME_LENGTH];
		char			entry[64];

		ci = &cgs.clientinfo[spectatorClients[i]];
		Q_strncpyz( cleanName, ci->name, sizeof( cleanName ) );
		Q_CleanStr( cleanName );
		if ( !cleanName[0] ) {
			Q_strncpyz( cleanName, "UnnamedPlayer", sizeof( cleanName ) );
		}

		if ( cgs.gametype == GT_TOURNAMENT ) {
			if ( ci->spectateOnly ) {
				Com_sprintf( entry, sizeof( entry ), "^7(^5s^7) %s", cleanName );
			} else if ( ci->spectatorQueuePosition > 0 ) {
				Com_sprintf( entry, sizeof( entry ), "(%d) %s", ci->spectatorQueuePosition, cleanName );
			} else {
				Q_strncpyz( entry, cleanName, sizeof( entry ) );
			}
		} else {
			Q_strncpyz( entry, cleanName, sizeof( entry ) );
		}

		Q_strncpyz( newSpectatorEntries[i], entry, sizeof( newSpectatorEntries[i] ) );
	}

	cacheChanged = ( strcmp( cg.spectatorList, newSpectatorList ) != 0 );
	if ( !cacheChanged && cg.spectatorEntryCount != newEntryCount ) {
		cacheChanged = qtrue;
	}
	if ( !cacheChanged ) {
		for ( i = 0; i < newEntryCount; i++ ) {
			if ( strcmp( cg.spectatorEntries[i], newSpectatorEntries[i] ) != 0 ) {
				cacheChanged = qtrue;
				break;
			}
		}
	}

	Q_strncpyz( cg.spectatorList, newSpectatorList, sizeof( cg.spectatorList ) );
	memcpy( cg.spectatorEntries, newSpectatorEntries, sizeof( cg.spectatorEntries ) );
	cg.spectatorEntryCount = newEntryCount;
	cg.spectatorLen = strlen( cg.spectatorList );

	if ( cacheChanged ) {
		cg.spectatorWidth = -1;
		cg.spectatorOffset = 0;
		cg.spectatorPaintX = 0;
		cg.spectatorPaintX2 = 0;
		cg.spectatorPaintLen = 0;
		cg.spectatorTime = 0;
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

Returns a bounds-checked configstring pointer out of the client game state.
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

Parses the music configstring and starts the paired intro/loop track.
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

/*
=============
CG_GetMenuBuffer

Loads a HUD menu text file into the shared menu buffer.
=============
*/
char *CG_GetMenuBuffer( const char *filename ) {
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

/*
=============
CG_Asset_Parse

Parses the global HUD asset block used by the menu parser.
=============
*/
qboolean CG_Asset_Parse( int handle ) {
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

/*
=============
CG_ParseMenu

Parses one HUD menu source through the retail cgame-owned browser/menu bridge.
=============
*/
void CG_ParseMenu( const char *menuFile ) {
	pc_token_t	token;
	int			handle;

	handle = trap_PC_LoadSource( menuFile );
	if ( !handle ) {
		handle = trap_PC_LoadSource( "ui/testhud.menu" );
	}
	if ( !handle ) {
		return;
	}

	while ( 1 ) {
		if ( !trap_PC_ReadToken( handle, &token ) ) {
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

		if ( Q_stricmp( token.string, "assetGlobalDef" ) == 0 ) {
			if ( CG_Asset_Parse( handle ) ) {
				continue;
			} else {
				break;
			}
		}


		if ( Q_stricmp( token.string, "menudef" ) == 0 ) {
			menuDef_t	*menu;

			if ( menuCount >= MAX_MENUS ) {
				break;
			}

			menu = &Menus[menuCount];
			CG_InitBrowserOverlay( menu );
			if ( CG_ParseBrowserMenu( handle, menu ) ) {
				Menu_PostParse( menu );
				menuCount++;
			}
		}
	}
	trap_PC_FreeSource( handle );
}

/*
=============
CG_Load_Menu

Walks a retail loadmenu block and parses each nested menu source.
=============
*/
qboolean CG_Load_Menu( char **p ) {
	char	*token;

	token = COM_ParseExt( p, qtrue );

	if ( token[0] != '{' ) {
		return qfalse;
	}

	while ( 1 ) {

		token = COM_ParseExt( p, qtrue );

		if ( Q_stricmp( token, "}" ) == 0 ) {
			return qtrue;
		}

		if ( !token || token[0] == 0 ) {
			return qfalse;
		}

		CG_ParseMenu( token );
	}
	return qfalse;
}

/*
=============
CG_BrowserValueIsNumeric

Matches the retail numeric-string probe used by browser preset validation.
=============
*/
static qboolean CG_BrowserValueIsNumeric( const char *text ) {
	qboolean	sawDecimal;

	if ( text == NULL || *text == '\0' ) {
		return qfalse;
	}

	sawDecimal = qfalse;
	while ( *text ) {
		if ( *text >= '0' && *text <= '9' ) {
			text++;
			continue;
		}

		if ( *text == '.' ) {
			if ( sawDecimal ) {
				return qfalse;
			}

			sawDecimal = qtrue;
			text++;
			continue;
		}

		return qfalse;
	}

	return qtrue;
}

/*
=============
CG_BrowserPresetValueMatchesCvar

Compares a browser preset entry against the live cvar state, including the
retail epsilon float fallback for numeric strings.
=============
*/
static qboolean CG_BrowserPresetValueMatchesCvar( const char *cvarName, const char *presetValue, float presetNumericValue ) {
	char	currentValue[64];

	if ( cvarName == NULL || presetValue == NULL ) {
		return qfalse;
	}

	trap_Cvar_VariableStringBuffer( cvarName, currentValue, sizeof( currentValue ) );
	if ( Q_stricmp( currentValue, presetValue ) == 0 ) {
		return qtrue;
	}

	if ( !CG_BrowserValueIsNumeric( currentValue ) || !CG_BrowserValueIsNumeric( presetValue ) ) {
		return qfalse;
	}

	return fabs( trap_Cvar_VariableValue( cvarName ) - presetNumericValue ) <= 0.001f;
}

/*
=============
CG_UpdateBrowserPresetLists

Refreshes retail browser preset-list labels against the linked live cvars.
=============
*/
void CG_UpdateBrowserPresetLists( void *overlay ) {
	char		currentPreset[1024];
	int		i;
	menuDef_t	*menu;

	menu = (menuDef_t *)overlay;
	if ( menu == NULL ) {
		return;
	}

	for ( i = 0; i < menu->itemCount; i++ ) {
		int		j;
		int		presetIndex;
		itemDef_t	*item;
		itemDef_t	*presetItem;
		multiDef_t	*presetList;
		multiDef_t	*presetValues;

		item = menu->items[i];
		if ( item == NULL || item->type != ITEM_TYPE_PRESETLIST || item->cvar == NULL || item->typeData == NULL ) {
			continue;
		}

		presetList = (multiDef_t *)item->typeData;
		trap_Cvar_VariableStringBuffer( item->cvar, currentPreset, sizeof( currentPreset ) );

		for ( presetIndex = 0; presetIndex < presetList->count; presetIndex++ ) {
			if ( presetList->cvarList[presetIndex] == NULL ||
				Q_stricmp( presetList->cvarList[presetIndex], currentPreset ) != 0 ) {
				continue;
			}

			presetItem = Menu_FindItemByName( menu, presetList->cvarStr[presetIndex] );
			if ( presetItem == NULL || presetItem->typeData == NULL ) {
				break;
			}

			presetValues = (multiDef_t *)presetItem->typeData;
			for ( j = 0; j < presetValues->count; j++ ) {
				if ( !CG_BrowserPresetValueMatchesCvar( presetValues->cvarList[j], presetValues->cvarStr[j], presetValues->cvarValue[j] ) ) {
					trap_Cvar_Set( item->cvar, "Custom" );
					break;
				}
			}

			break;
		}
	}
}

/*
=============
CG_UpdateBrowserWidgetPositions

Refreshes retail browser widget screen-space rectangles through the shared menu
layout helper.
=============
*/
void CG_UpdateBrowserWidgetPositions( void *overlay ) {
	if ( overlay == NULL ) {
		return;
	}

	Menu_UpdatePosition( (menuDef_t *)overlay );
}

/*
=============
CG_FindBrowserOverlayByName

Finds a retail browser overlay root by name through the shared menu registry.
=============
*/
void *CG_FindBrowserOverlayByName( const char *name ) {
	if ( name == NULL || !name[0] ) {
		return NULL;
	}

	return Menus_FindByName( name );
}

/*
=============
CG_OpenBrowserOverlayByName

Opens a retail browser overlay root and refreshes its live layout or preset
state through the shared menu runtime.
=============
*/
void *CG_OpenBrowserOverlayByName( const char *name ) {
	menuDef_t	*menu;

	menu = CG_FindBrowserOverlayByName( name );
	if ( menu == NULL ) {
		return NULL;
	}

	CG_ActivateBrowserOverlay( menu );
	CG_UpdateBrowserWidgetPositions( menu );
	CG_UpdateBrowserPresetLists( menu );
	return menu;
}

/*
=============
CG_CloseBrowserOverlayByName

Closes a retail browser overlay root and clears its forced-visibility latch.
=============
*/
void *CG_CloseBrowserOverlayByName( const char *name ) {
	menuDef_t	*menu;

	menu = CG_FindBrowserOverlayByName( name );
	if ( menu == NULL ) {
		return NULL;
	}

	Menus_CloseByName( name );
	menu->window.flags &= ~WINDOW_FORCED;
	return menu;
}

/*
=============
CG_InitBrowserOverlay

Initializes one browser overlay through the shared menu runtime entry point.
=============
*/
void CG_InitBrowserOverlay( void *overlay ) {
	Menu_Init( (menuDef_t *)overlay );
}

/*
=============
CG_SetupBrowserItemKeywordHash

Rebuilds the retail browser item keyword hash through the shared parser table.
=============
*/
void CG_SetupBrowserItemKeywordHash( void ) {
	Item_SetupKeywordHash();
}

/*
=============
CG_ParseBrowserItem

Routes the browser item parser through the shared menu runtime implementation.
=============
*/
qboolean CG_ParseBrowserItem( int handle, void *item ) {
	return Item_Parse( handle, (itemDef_t *)item );
}

/*
=============
CG_SetupBrowserMenuKeywordHash

Rebuilds the retail browser menu keyword hash through the shared parser table.
=============
*/
void CG_SetupBrowserMenuKeywordHash( void ) {
	Menu_SetupKeywordHash();
}

/*
=============
CG_ParseBrowserMenu

Routes the browser menu parser through the shared menu runtime implementation.
=============
*/
qboolean CG_ParseBrowserMenu( int handle, void *menu ) {
	return Menu_Parse( handle, (menuDef_t *)menu );
}

/*
=============
CG_InitBrowserRuntime

Rebuilds the shared browser/menu parser runtime before HUD loads and reloads.
=============
*/
void CG_InitBrowserRuntime( void ) {
	String_Init();
	CG_SetupBrowserItemKeywordHash();
	CG_SetupBrowserMenuKeywordHash();
}

/*
=============
CG_ResetBrowserOverlayState

Clears the shared browser/menu state and drops cached cgame overlay pointers.
=============
*/
void CG_ResetBrowserOverlayState( void ) {
	Menu_Reset();
	CG_ResetDraw2DMenuCache();
	CG_ResetJoinGameMenuCaptureState();
}

static const char *const cgRetailSupplementalMenuFiles[] = {
	"ui/intro.menu",
	"ui/ingamescoreteam.menu",
	"ui/ingamescorenoteam.menu",
	"ui/endscoreteam.menu",
	"ui/endscorenoteam.menu",
	"ui/spectator.menu",
	"ui/spectator_follow.menu",
	"ui/comp_spectator.menu",
	"ui/comp_spectator_follow.menu",
	"ui/ingamestats.menu",
	"ui/ingame_scoreboard_ffa.menu",
	"ui/ingame_scoreboard_duel.menu",
	"ui/ingame_scoreboard_race.menu",
	"ui/ingame_scoreboard_tdm.menu",
	"ui/ingame_scoreboard_ca.menu",
	"ui/ingame_scoreboard_ctf.menu",
	"ui/ingame_scoreboard_1fctf.menu",
	"ui/ingame_scoreboard_har.menu",
	"ui/ingame_scoreboard_ft.menu",
	"ui/ingame_scoreboard_dom.menu",
	"ui/ingame_scoreboard_ad.menu",
	"ui/ingame_scoreboard_rr.menu",
	"ui/end_scoreboard_ffa.menu",
	"ui/end_scoreboard_duel.menu",
	"ui/end_scoreboard_race.menu",
	"ui/end_scoreboard_tdm.menu",
	"ui/end_scoreboard_ca.menu",
	"ui/end_scoreboard_ctf.menu",
	"ui/end_scoreboard_1fctf.menu",
	"ui/end_scoreboard_har.menu",
	"ui/end_scoreboard_ft.menu",
	"ui/end_scoreboard_dom.menu",
	"ui/end_scoreboard_ad.menu",
	"ui/end_scoreboard_rr.menu"
};

/*
=============
CG_LoadMenus

Loads the selected HUD script and any retail supplemental menu files.
=============
*/
void CG_LoadMenus( const char *menuFile ) {
	char			*token;
	char			*p;
	int				i;
	int				len;
	int				start;
	fileHandle_t	f;
	static char		buf[MAX_MENUDEFFILE];

	start = trap_Milliseconds();

	len = trap_FS_FOpenFile( menuFile, &f, FS_READ );
	if ( !f ) {
		CG_Printf( S_COLOR_YELLOW "menu file not found: %s, using default\n", menuFile );
		len = trap_FS_FOpenFile( CG_LEGACY_HUD_FILE, &f, FS_READ );
		if ( !f ) {
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

	COM_Compress( buf );

	CG_ResetBrowserOverlayState();

	for ( i = 0; i < ARRAY_LEN( cgRetailSupplementalMenuFiles ); i++ ) {
		// Current public HUD scripts already inline part of the retail set.
		// Skip any supplemental file already named in the selected HUD script.
		if ( strstr( buf, cgRetailSupplementalMenuFiles[i] ) ) {
			continue;
		}

		CG_ParseMenu( cgRetailSupplementalMenuFiles[i] );
	}

	p = buf;

	while ( 1 ) {
		token = COM_ParseExt( &p, qtrue );
		if ( !token || token[0] == 0 || token[0] == '}' ) {
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

		if ( Q_stricmp( token, "loadmenu" ) == 0 ) {
			if ( CG_Load_Menu( &p ) ) {
				continue;
			} else {
				break;
			}
		}
	}

	Com_Printf( "UI menu load time = %d milli seconds\n", trap_Milliseconds() - start );

}

/*
=============
CG_SetBrowserFeederSelection

Bridges retail browser feeder-selection calls onto the shared menu runtime.
=============
*/
void CG_SetBrowserFeederSelection( void *overlay, int feeder, int index ) {
	Menu_SetFeederSelection( (menuDef_t *)overlay, feeder, index, NULL );
}



/*
=============
CG_OwnerDrawHandleKey

Retail null key handler reused by the display-context ownerdraw callbacks.
=============
*/
static qboolean CG_OwnerDrawHandleKey( int ownerDraw, int flags, float *special, int key ) {
	return qfalse;
}

/*
=============
CG_FindScoreIndexForClient

Maps a client number back to its score index for feeder lookups.
=============
*/
static int CG_FindScoreIndexForClient( int clientNum ) {
	int		i;

	for ( i = 0; i < cg.numScores; i++ ) {
		if ( cg.scores[i].client == clientNum ) {
			return i;
		}
	}

	return -1;
}

typedef struct {
	int					team;
	int					scoreIndex;
	int					clientNum;
	clientInfo_t			*info;
	score_t				*scoreRow;
	const cgHudScoreboardEntry_t	*hudEntry;
	qhandle_t				socialHandle;
} cgFeederRow_t;

/*
=============
CG_IsScoreboardFeeder

Returns qtrue when the feeder id targets a non-team scoreboard list.
=============
*/
static qboolean CG_IsScoreboardFeeder( float feederID ) {
	return ( feederID == FEEDER_SCOREBOARD || feederID == FEEDER_ENDSCOREBOARD ) ? qtrue : qfalse;
}

/*
=============
CG_IsTeamListFeeder

Returns qtrue when the feeder id targets a retail red or blue team list.
=============
*/
static qboolean CG_IsTeamListFeeder( float feederID ) {
	return ( feederID == FEEDER_REDTEAM_LIST || feederID == FEEDER_BLUETEAM_LIST ) ? qtrue : qfalse;
}

/*
=============
CG_IsTeamStatsFeeder

Returns qtrue when the feeder id targets one of the rich end-score team stats
lists.
=============
*/
static qboolean CG_IsTeamStatsFeeder( float feederID ) {
	return ( feederID == FEEDER_REDTEAM_STATS || feederID == FEEDER_BLUETEAM_STATS ) ? qtrue : qfalse;
}

/*
=============
CG_GetFeederTeam

Returns the team backing the current feeder, or -1 for non-team scoreboards.
=============
*/
static int CG_GetFeederTeam( float feederID ) {
	if ( feederID == FEEDER_REDTEAM_LIST || feederID == FEEDER_REDTEAM_STATS ) {
		return TEAM_RED;
	}

	if ( feederID == FEEDER_BLUETEAM_LIST || feederID == FEEDER_BLUETEAM_STATS ) {
		return TEAM_BLUE;
	}

	return -1;
}

/*
=============
CG_ScoreIndexFromTeamRow

Maps a team-list local row back to the absolute cg.scores row used by cgame.
=============
*/
static int CG_ScoreIndexFromTeamRow( int teamRow, int team ) {
	int		i;
	int		count;

	if ( teamRow < 0 ) {
		return -1;
	}

	if ( team != TEAM_RED && team != TEAM_BLUE ) {
		return ( teamRow < cg.numScores ) ? teamRow : -1;
	}

	count = 0;
	for ( i = 0; i < cg.numScores; i++ ) {
		if ( cg.scores[i].team != team ) {
			continue;
		}

		if ( count == teamRow ) {
			return i;
		}

		count++;
	}

	return -1;
}

/*
=============
CG_TeamRowFromScoreIndex

Maps an absolute cg.scores row to the retail team-list local row.
=============
*/
static int CG_TeamRowFromScoreIndex( int scoreIndex, int team ) {
	int		i;
	int		count;

	if ( scoreIndex < 0 || scoreIndex >= cg.numScores ) {
		return -1;
	}

	if ( team != TEAM_RED && team != TEAM_BLUE ) {
		return scoreIndex;
	}

	count = 0;
	for ( i = 0; i < cg.numScores; i++ ) {
		if ( cg.scores[i].team != team ) {
			continue;
		}

		if ( i == scoreIndex ) {
			return count;
		}

		count++;
	}

	return -1;
}

/*
=============
CG_FeederCount

Returns the live row count for retail scoreboard, team-list, and team-stats
feeders.
=============
*/
static int CG_FeederCount( float feederID ) {
	int i, count;
	count = 0;

	if ( cg.competitiveHudLoaded ) {
		CG_BuildHudScoreboard();
	}
	if ( feederID == FEEDER_REDTEAM_LIST || feederID == FEEDER_REDTEAM_STATS ) {
		if ( cg.competitiveHudLoaded ) {
			return CG_GetHudScoreboardTeamCount( TEAM_RED );
		}
		for ( i = 0; i < cg.numScores; i++ ) {
			if ( cg.scores[i].team == TEAM_RED ) {
				count++;
			}
		}
	} else if ( feederID == FEEDER_BLUETEAM_LIST || feederID == FEEDER_BLUETEAM_STATS ) {
		if ( cg.competitiveHudLoaded ) {
			return CG_GetHudScoreboardTeamCount( TEAM_BLUE );
		}
		for ( i = 0; i < cg.numScores; i++ ) {
			if ( cg.scores[i].team == TEAM_BLUE ) {
				count++;
			}
		}
	} else if ( CG_IsScoreboardFeeder( feederID ) ) {
		if ( cg.competitiveHudLoaded ) {
			const cgHudScoreboard_t *hud = CG_GetHudScoreboard();
			return hud ? hud->count : 0;
		}
		return cg.numScores;
	}
	return count;
}


/*
=============
CG_SetScoreSelection

Synchronizes the active scoreboard row into the matching browser feeder.
=============
*/
void CG_SetScoreSelection( void *p ) {
	menuDef_t		*menu;
	playerState_t	*ps;
	int				i;

	menu = (menuDef_t *)p;
	ps = &cg.snap->ps;

	for ( i = 0; i < cg.numScores; i++ ) {
		if ( ps->clientNum == cg.scores[i].client ) {
			cg.selectedScore = i;
			break;
		}
	}

	if ( menu == NULL ) {
		return;
	}

	if ( cg.selectedScore < 0 || cg.selectedScore >= cg.numScores ) {
		return;
	}

	if ( cgs.gametype >= GT_TEAM ) {
		int feeder = FEEDER_REDTEAM_LIST;
		int teamIndex;

		if ( cg.scores[cg.selectedScore].team == TEAM_BLUE ) {
			feeder = FEEDER_BLUETEAM_LIST;
		}

		teamIndex = CG_TeamRowFromScoreIndex( cg.selectedScore, cg.scores[cg.selectedScore].team );
		if ( teamIndex >= 0 ) {
			CG_SetBrowserFeederSelection( menu, feeder, teamIndex );
		}
	} else {
		CG_SetBrowserFeederSelection( menu, FEEDER_SCOREBOARD, cg.selectedScore );
	}
}

/*
=============
CG_GetScoreboardSelectionMenuName

Returns the live or end-scoreboard menu name that retail caches for the
team-list selection seam.
=============
*/
static const char *CG_GetScoreboardSelectionMenuName( qboolean endScoreboard ) {
	if ( endScoreboard ) {
		switch ( cgs.gametype ) {
		case GT_FFA:
			return "endscore_menu_ffa";
		case GT_TOURNAMENT:
			return "endscore_menu_duel";
		case GT_SINGLE_PLAYER:
#if GT_RACE != GT_SINGLE_PLAYER
		case GT_RACE:
#endif
			return "endscore_menu_race";
		case GT_RED_ROVER:
			return "endscore_menu_rr";
		case GT_TEAM:
			return "endteamscore_menu_tdm";
		case GT_CLAN_ARENA:
			return "endteamscore_menu_ca";
		case GT_CTF:
			return "endteamscore_menu_ctf";
		case GT_1FCTF:
			return "endteamscore_menu_1fctf";
		case GT_HARVESTER:
			return "endteamscore_menu_har";
		case GT_FREEZE:
			return "endteamscore_menu_ft";
		case GT_DOMINATION:
			return "endteamscore_menu_dom";
		case GT_ATTACK_DEFEND:
			return "endteamscore_menu_ad";
		default:
			break;
		}

		if ( cgs.gametype >= GT_TEAM ) {
			return "endscoreteam";
		}

		return "endscorenoteam";
	}

	switch ( cgs.gametype ) {
	case GT_FFA:
		return "score_menu_ffa";
	case GT_TOURNAMENT:
		return "score_menu_duel";
	case GT_SINGLE_PLAYER:
#if GT_RACE != GT_SINGLE_PLAYER
	case GT_RACE:
#endif
		return "score_menu_race";
	case GT_RED_ROVER:
		return "score_menu_rr";
	case GT_TEAM:
		return "teamscore_menu_tdm";
	case GT_CLAN_ARENA:
		return "teamscore_menu_ca";
	case GT_CTF:
		return "teamscore_menu_ctf";
	case GT_1FCTF:
		return "teamscore_menu_1fctf";
	case GT_OBELISK:
		return "teamscore_menu";
	case GT_HARVESTER:
		return "teamscore_menu_har";
	case GT_FREEZE:
		return "teamscore_menu_ft";
	case GT_DOMINATION:
		return "teamscore_menu_dom";
	case GT_ATTACK_DEFEND:
		return "teamscore_menu_ad";
	default:
		break;
	}

	if ( cgs.gametype >= GT_TEAM ) {
		return "teamscore_menu";
	}

	return "score_menu";
}

/*
=============
CG_CacheScoreboardSelectionMenus

Caches the live and end-scoreboard menu roots that retail reuses for team-list
selection synchronization.
=============
*/
static void CG_CacheScoreboardSelectionMenus( void ) {
	const char	*liveMenuName;
	const char	*endMenuName;

	cgScoreboardSelectionMenus[0] = NULL;
	cgScoreboardSelectionMenus[1] = NULL;

	if ( !cg.competitiveHudLoaded ) {
		return;
	}

	liveMenuName = CG_GetScoreboardSelectionMenuName( qfalse );
	endMenuName = CG_GetScoreboardSelectionMenuName( qtrue );

	if ( liveMenuName ) {
		cgScoreboardSelectionMenus[0] = CG_FindBrowserOverlayByName( liveMenuName );
	}
	if ( endMenuName ) {
		cgScoreboardSelectionMenus[1] = CG_FindBrowserOverlayByName( endMenuName );
	}
}

/*
=============
CG_FindScoreboardTeamListItem

Finds a named red/blue team-list item inside a cached scoreboard menu.
=============
*/
static itemDef_t *CG_FindScoreboardTeamListItem( menuDef_t *menu, const char *itemName ) {
	int			i;
	itemDef_t	*item;

	if ( !menu || !itemName || !itemName[0] ) {
		return NULL;
	}

	for ( i = 0; i < menu->itemCount; i++ ) {
		item = menu->items[i];
		if ( !item || !item->window.name ) {
			continue;
		}

		if ( !Q_stricmp( item->window.name, itemName ) ) {
			return item;
		}
	}

	return NULL;
}

/*
=============
CG_SetScoreboardTeamListCursor

Applies the retail team-list cursor update to a cached scoreboard menu item.
=============
*/
static void CG_SetScoreboardTeamListCursor( menuDef_t *menu, const char *itemName, int index ) {
	itemDef_t		*item;
	listBoxDef_t	*listPtr;

	item = CG_FindScoreboardTeamListItem( menu, itemName );
	if ( !item ) {
		return;
	}

	item->cursorPos = index;

	if ( index >= 0 && item->typeData ) {
		listPtr = (listBoxDef_t *)item->typeData;
		listPtr->cursorPos = index;
	}
}

/*
=============
CG_SyncScoreboardTeamListSelection

Keeps the cached live and end-scoreboard team-list cursors aligned with the
current retail feeder selection.
=============
*/
static void CG_SyncScoreboardTeamListSelection( team_t team, int index ) {
	const char	*selectedItemName;
	const char	*clearedItemName;
	int			i;

	selectedItemName = ( team == TEAM_RED ) ? "playerlistRED" : "playerlistBLUE";
	clearedItemName = ( team == TEAM_RED ) ? "playerlistBLUE" : "playerlistRED";

	for ( i = 0; i < ARRAY_LEN( cgScoreboardSelectionMenus ); i++ ) {
		CG_SetScoreboardTeamListCursor( cgScoreboardSelectionMenus[i], selectedItemName, index );
		CG_SetScoreboardTeamListCursor( cgScoreboardSelectionMenus[i], clearedItemName, -1 );
	}
}

/*
=============
CG_InfoFromScoreIndex

Maps a feeder-local row back to the absolute score row and client info.
=============
*/
static clientInfo_t *CG_InfoFromScoreIndex( int index, int team, int *scoreIndex ) {
	int		i;
	int		count;

	if ( scoreIndex ) {
		*scoreIndex = -1;
	}

	if ( index < 0 ) {
		return NULL;
	}

	if ( cg.competitiveHudLoaded ) {
		const cgHudScoreboardEntry_t		*entry;
		int		mappedIndex;

		CG_BuildHudScoreboard();
		entry = CG_GetHudScoreboardEntry( index, team );
		if ( entry ) {
			mappedIndex = CG_FindScoreIndexForClient( entry->clientNum );
			if ( mappedIndex >= 0 ) {
				if ( scoreIndex ) {
					*scoreIndex = mappedIndex;
				}
				return &cgs.clientinfo[entry->clientNum];
			}
		}
	}

	if ( cgs.gametype >= GT_TEAM && ( team == TEAM_RED || team == TEAM_BLUE ) ) {
		count = 0;
		for ( i = 0; i < cg.numScores; i++ ) {
			if ( cg.scores[i].team == team ) {
				if ( count == index ) {
					if ( scoreIndex ) {
						*scoreIndex = i;
					}
					return &cgs.clientinfo[cg.scores[i].client];
				}
				count++;
			}
		}
	}

	if ( index >= cg.numScores ) {
		return NULL;
	}

	if ( scoreIndex ) {
		*scoreIndex = index;
	}
	return &cgs.clientinfo[ cg.scores[index].client ];
}

/*
=============
CG_IsClientMutedLocally

Mirrors the retail scoreboard social-icon lookup through the native mute import.
=============
*/
static qboolean CG_IsClientMutedLocally( int clientNum ) {
	const clientInfo_t *ci;

	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return qfalse;
	}

	ci = &cgs.clientinfo[clientNum];
	if ( ci->identityLow || ci->identityHigh ) {
		cg.clientMuted[clientNum] = trap_QL_IsClientMuted( ci->identityLow, ci->identityHigh ) ? qtrue : qfalse;
	}

	return cg.clientMuted[clientNum];
}

/*
=============
CG_FeederSocialHandle

Returns the retail-backed social overlay icon for a scoreboard client row.
=============
*/
static qhandle_t CG_FeederSocialHandle( int clientNum ) {
	const cgClientSpeakingState_t	*speakingState;

	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return 0;
	}

	if ( CG_IsClientMutedLocally( clientNum ) ) {
		return cgs.media.scoreMutedShader;
	}

	if ( !CG_ShouldDisplayVoiceIndicator() ) {
		return 0;
	}
	speakingState = &cgClientSpeakingState[clientNum];
	if ( !speakingState->speaking ) {
		return 0;
	}
	if ( speakingState->time <= 0 ) {
		return 0;
	}
	if ( cg.time - speakingState->time > 2500 ) {
		return 0;
	}

	return cgs.media.scoreSpeakingShader;
}

/*
=============
CG_BuildFeederRow

Builds the shared row context used by the reconstructed retail feeder leaves.
=============
*/
static qboolean CG_BuildFeederRow( int index, int team, cgFeederRow_t *row ) {
	if ( !row ) {
		return qfalse;
	}

	memset( row, 0, sizeof( *row ) );
	row->team = team;
	row->scoreIndex = -1;
	row->clientNum = -1;
	row->info = CG_InfoFromScoreIndex( index, team, &row->scoreIndex );

	if ( !row->info ) {
		return qfalse;
	}

	if ( row->scoreIndex >= 0 && row->scoreIndex < cg.numScores ) {
		row->scoreRow = &cg.scores[row->scoreIndex];
	}

	if ( cg.competitiveHudLoaded ) {
		row->hudEntry = CG_GetHudScoreboardEntry( index, team );
	}

	if ( row->hudEntry ) {
		row->clientNum = row->hudEntry->clientNum;
	} else if ( row->scoreRow ) {
		row->clientNum = row->scoreRow->client;
	}

	row->socialHandle = CG_FeederSocialHandle( row->clientNum );
	return qtrue;
}

/*
=============
CG_FeederCountryFlagHandle

Returns the already-cached country flag when available, falling back to the
retail country-code registration path for feeder-only rows.
=============
*/
static qhandle_t CG_FeederCountryFlagHandle( const clientInfo_t *ci ) {
	if ( !ci ) {
		return 0;
	}

	if ( ci->countryFlagShader ) {
		return ci->countryFlagShader;
	}

	return CG_RegisterCountryFlag( ci->country );
}

/*
=============
CG_FeederPowerupHandle

Finds the first retail scoreboard powerup icon for a row, matching the
non-neutral powerup scan used by the Quake Live cgame feeder.
=============
*/
static qhandle_t CG_FeederPowerupHandle( int powerups ) {
	int			powerup;
	gitem_t		*item;

	if ( !powerups ) {
		return 0;
	}

	for ( powerup = PW_QUAD; powerup < PW_NUM_POWERUPS; powerup++ ) {
		if ( powerup == PW_NEUTRALFLAG ) {
			continue;
		}
		if ( !( powerups & ( 1 << powerup ) ) ) {
			continue;
		}

		item = BG_FindItemForPowerup( (powerup_t)powerup );
		if ( item && item->icon ) {
			return trap_R_RegisterShaderNoMip( item->icon );
		}
	}

	return 0;
}

/*
=============
CG_FeederClientReady

Returns qtrue when the scoreboard row client is marked ready in the snapshot.
=============
*/
static qboolean CG_FeederClientReady( const cgFeederRow_t *row ) {
	if ( !row || !cg.snap || row->clientNum < 0 || row->clientNum >= MAX_CLIENTS ) {
		return qfalse;
	}

	return ( cg.snap->ps.stats[ STAT_CLIENTS_READY ] & ( 1 << row->clientNum ) ) ? qtrue : qfalse;
}

/*
=============
CG_FeederShouldShowReadyIcon

Matches the retail branch that swaps the powerup column for ready-state arrows
during warmup ready-up or intermission exit voting.
=============
*/
static qboolean CG_FeederShouldShowReadyIcon( void ) {
	if ( !cg.snap ) {
		return qfalse;
	}

	if ( cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return qtrue;
	}

	if ( cgs.matchReadyUpDeadline > 0 || cgs.matchWarmupReadyEligible > 0 ||
		 cgs.intermissionExitStatusLatched ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_FeederReadyHandle

Returns the retail green/red ready-state arrow shader for the row.
=============
*/
static qhandle_t CG_FeederReadyHandle( const cgFeederRow_t *row ) {
	return CG_FeederClientReady( row ) ? cgs.media.scoreArrowGreenShader : cgs.media.scoreArrowRedShader;
}

/*
=============
CG_FeederScoreValue

Formats retail scoreboard scores, including Quake Live's absent/forfeit dash.
=============
*/
static const char *CG_FeederScoreValue( int score ) {
	if ( score == SCORE_NOT_PRESENT || score == -999 ) {
		return "-";
	}

	return va( "%i", score );
}

/*
=============
CG_FeederFormattedDamage

Formats damage with the compact thousands suffix used by retail scoreboards.
=============
*/
static const char *CG_FeederFormattedDamage( int damage ) {
	if ( damage < 1000 ) {
		return va( "%i", damage );
	}

	if ( damage >= 10000 ) {
		return va( "%2.0fK", (float)damage / 1000.0f );
	}

	return va( "%1.1fK", (float)damage / 1000.0f );
}

/*
=============
CG_FeederBestWeaponHandle

Returns the best-weapon icon for rows with weapon damage attribution.
=============
*/
static qhandle_t CG_FeederBestWeaponHandle( const score_t *score ) {
	if ( !score || score->damage <= 0 || score->bestWeapon <= WP_NONE ||
		 score->bestWeapon >= MAX_WEAPONS ) {
		return 0;
	}

	return cg_weapons[ score->bestWeapon ].weaponIcon;
}

/*
=============
CG_FeederFormatRaceTime

Formats the race scoreboard best-time value as Quake Live's mm:ss.mmm text.
=============
*/
static const char *CG_FeederFormatRaceTime( int milliseconds ) {
	int		minutes;
	int		seconds;
	int		millis;

	if ( milliseconds <= 0 ) {
		return "-";
	}

	minutes = milliseconds / 60000;
	seconds = ( milliseconds % 60000 ) / 1000;
	millis = milliseconds % 1000;

	return va( "%i:%02i.%03i", minutes, seconds, millis );
}

/*
=============
CG_FeederItemTextScoreboard

Formats the retail non-team scoreboard and end-score feeder leaves.
=============
*/
static const char *CG_FeederItemTextScoreboard( int index, int column, qhandle_t *handle ) {
	cgFeederRow_t	row;
	qhandle_t		icon;
	int				score;
	int				time;
	int				ping;

	if ( !CG_BuildFeederRow( index, -1, &row ) ) {
		return "";
	}
	if ( !row.info || !row.info->infoValid || row.info->team == TEAM_SPECTATOR ) {
		return "";
	}

	switch ( column ) {
	case 0:
		*handle = CG_FeederCountryFlagHandle( row.info );
		return "";
	case 1:
		if ( row.socialHandle ) {
			*handle = row.socialHandle;
		}
		return "";
	case 2:
		if ( row.info->handicap < 100 ) {
			return va( "%i", row.info->handicap );
		}
		return "";
	case 3:
		if ( CG_FeederShouldShowReadyIcon() ) {
			icon = CG_FeederReadyHandle( &row );
		} else {
			icon = CG_FeederPowerupHandle( row.info->powerups );
		}
		if ( icon ) {
			*handle = icon;
		}
		return "";
	case 4:
		*handle = CG_FeederCountryFlagHandle( row.info );
		return "";
	case 5:
		return row.info->name;
	case 6:
		if ( cgs.gametype == GT_TOURNAMENT ) {
			return va( "%i/%i", row.info->wins, row.info->losses );
		}
		return "";
	case 7:
		score = row.scoreRow ? row.scoreRow->score : ( row.hudEntry ? row.hudEntry->score : row.info->score );
		return CG_FeederScoreValue( score );
	case 8:
		if ( row.scoreRow ) {
			return va( "%i/%i", row.scoreRow->kills, row.scoreRow->deaths );
		}
		return "";
	case 9:
		if ( row.scoreRow ) {
			return CG_FeederFormattedDamage( row.scoreRow->damage );
		}
		return "";
	case 10:
		icon = CG_FeederBestWeaponHandle( row.scoreRow );
		if ( icon ) {
			*handle = icon;
		}
		return "";
	case 11:
		if ( row.scoreRow && CG_FeederBestWeaponHandle( row.scoreRow ) ) {
			return va( "%i%%", row.scoreRow->accuracy );
		}
		return "";
	case 12:
		time = row.scoreRow ? row.scoreRow->time : ( row.hudEntry ? row.hudEntry->time : 0 );
		return va( "%4i", time );
	case 13:
		ping = row.scoreRow ? row.scoreRow->ping : ( row.hudEntry ? row.hudEntry->ping : 0 );
		return va( "%4i", ping );
	}

	return "";
}

/*
=============
CG_FeederItemTextRaceScoreboard

Formats the dedicated retail race scoreboard feeder leaf.
=============
*/
static const char *CG_FeederItemTextRaceScoreboard( int index, int column, qhandle_t *handle ) {
	cgFeederRow_t	row;
	qhandle_t		icon;
	int				score;
	int				time;
	int				ping;

	if ( !CG_BuildFeederRow( index, -1, &row ) ) {
		return "";
	}
	if ( !row.info || !row.info->infoValid || row.info->team == TEAM_SPECTATOR ) {
		return "";
	}

	switch ( column ) {
	case 0:
		*handle = CG_FeederCountryFlagHandle( row.info );
		return "";
	case 1:
		if ( row.socialHandle ) {
			*handle = row.socialHandle;
		}
		return "";
	case 2:
		if ( CG_FeederShouldShowReadyIcon() ) {
			icon = CG_FeederReadyHandle( &row );
			if ( icon ) {
				*handle = icon;
			}
		}
		return "";
	case 3:
		return row.info->name;
	case 4:
		score = row.scoreRow ? row.scoreRow->score : ( row.hudEntry ? row.hudEntry->score : row.info->score );
		return CG_FeederFormatRaceTime( score );
	case 5:
		time = row.scoreRow ? row.scoreRow->time : ( row.hudEntry ? row.hudEntry->time : 0 );
		return va( "%4i", time );
	case 6:
		ping = row.scoreRow ? row.scoreRow->ping : ( row.hudEntry ? row.hudEntry->ping : 0 );
		return va( "%4i", ping );
	}

	return "";
}

/*
=============
CG_FeederItemTextTeamListLeadColumns

Formats the shared leading icon/name columns used by the retail team-list
feeder leaves.
=============
*/
static const char *CG_FeederItemTextTeamListLeadColumns( const cgFeederRow_t *row, int column, qhandle_t *handle ) {
	gitem_t		*item;

	if ( !row || !row->info || !row->info->infoValid ) {
		return "";
	}

	switch ( column ) {
	case 0:
		if ( row->info->powerups & ( 1 << PW_NEUTRALFLAG ) ) {
			item = BG_FindItemForPowerup( PW_NEUTRALFLAG );
			*handle = cg_items[ ITEM_INDEX( item ) ].icon;
		} else if ( row->info->powerups & ( 1 << PW_REDFLAG ) ) {
			item = BG_FindItemForPowerup( PW_REDFLAG );
			*handle = cg_items[ ITEM_INDEX( item ) ].icon;
		} else if ( row->info->powerups & ( 1 << PW_BLUEFLAG ) ) {
			item = BG_FindItemForPowerup( PW_BLUEFLAG );
			*handle = cg_items[ ITEM_INDEX( item ) ].icon;
		} else if ( row->info->botSkill > 0 && row->info->botSkill <= 5 ) {
			*handle = cgs.media.botSkillShaders[ row->info->botSkill - 1 ];
		} else if ( row->info->handicap < 100 ) {
			return va( "%i", row->info->handicap );
		}
		return "";
	case 1:
		*handle = CG_StatusHandle( row->info->teamTask );
		if ( *handle <= 0 && row->socialHandle ) {
			*handle = row->socialHandle;
		}
		return "";
	case 2:
		if ( row->clientNum >= 0 &&
			 ( cg.snap->ps.stats[ STAT_CLIENTS_READY ] & ( 1 << row->clientNum ) ) ) {
			return "Ready";
		}
		if ( row->info->teamLeader ) {
			return "Leader";
		}
		return "";
	case 3:
		if ( row->scoreRow && row->scoreRow->bestWeapon > WP_NONE &&
			 row->scoreRow->bestWeapon < MAX_WEAPONS &&
			 cg_weapons[ row->scoreRow->bestWeapon ].weaponIcon ) {
			*handle = cg_weapons[ row->scoreRow->bestWeapon ].weaponIcon;
		}
		return "";
	case 4:
		if ( row->scoreRow && row->scoreRow->activePlayer ) {
			return "*";
		}
		return "";
	case 5:
		return row->info->name;
	}

	return "";
}

/*
=============
CG_FeederItemTextFallbackTeamList

Conservative synthetic name for the generic retail team-list feeder leaf used
when the gametype does not select one of the richer per-family helpers.
=============
*/
static const char *CG_FeederItemTextFallbackTeamList( int team, int index, int column, qhandle_t *handle ) {
	cgFeederRow_t	row;

	if ( !CG_BuildFeederRow( index, team, &row ) ) {
		return "";
	}
	if ( !row.info || !row.info->infoValid || !row.scoreRow ) {
		return "";
	}

	if ( column <= 5 ) {
		return CG_FeederItemTextTeamListLeadColumns( &row, column, handle );
	}

	switch ( column ) {
	case 6:
		return va( "%i", row.scoreRow->score );
	case 7:
		return va( "%4i", row.scoreRow->time );
	case 8:
		if ( row.scoreRow->ping == -1 ) {
			return "connecting";
		}
		return va( "%4i", row.scoreRow->ping );
	}

	return "";
}

/*
=============
CG_FeederItemTextCTFFamilyTeamList

Formats the shared retail red/blue team-list feeder used by the CTF-family
modes.
=============
*/
static const char *CG_FeederItemTextCTFFamilyTeamList( int team, int index, int column, qhandle_t *handle ) {
	cgFeederRow_t	row;

	if ( !CG_BuildFeederRow( index, team, &row ) ) {
		return "";
	}
	if ( !row.info || !row.info->infoValid || !row.scoreRow ) {
		return "";
	}

	if ( column <= 5 ) {
		return CG_FeederItemTextTeamListLeadColumns( &row, column, handle );
	}

	switch ( column ) {
	case 6:
		return va( "%i", row.scoreRow->score );
	case 7:
		return va( "%i/%i", row.scoreRow->kills, row.scoreRow->deaths );
	case 8:
		return va( "%i", row.scoreRow->captures );
	case 9:
		return va( "%i", row.scoreRow->assistCount );
	case 10:
		return va( "%i", row.scoreRow->defendCount );
	case 11:
		return va( "%i%%", row.scoreRow->accuracy );
	}

	return "";
}

/*
=============
CG_FeederItemTextClanArenaTeamList

Formats the retail Clan Arena red/blue team-list feeder leaf.
=============
*/
static const char *CG_FeederItemTextClanArenaTeamList( int team, int index, int column, qhandle_t *handle ) {
	cgFeederRow_t	row;

	if ( !CG_BuildFeederRow( index, team, &row ) ) {
		return "";
	}
	if ( !row.info || !row.info->infoValid || !row.scoreRow ) {
		return "";
	}

	if ( column <= 5 ) {
		return CG_FeederItemTextTeamListLeadColumns( &row, column, handle );
	}

	switch ( column ) {
	case 6:
		return va( "%i", row.scoreRow->score );
	case 7:
		return va( "%i/%i", row.scoreRow->kills, row.scoreRow->deaths );
	case 8:
		return va( "%i", row.scoreRow->damage );
	case 9:
		if ( row.scoreRow->bestWeapon > WP_NONE &&
			 row.scoreRow->bestWeapon < MAX_WEAPONS &&
			 cg_weapons[ row.scoreRow->bestWeapon ].weaponIcon ) {
			*handle = cg_weapons[ row.scoreRow->bestWeapon ].weaponIcon;
		}
		return "";
	case 10:
		return va( "%i%%", row.scoreRow->accuracy );
	case 11:
		return va( "%4i", row.scoreRow->time );
	}

	return "";
}

/*
=============
CG_FeederItemTextTDMFreezeTeamList

Formats the retail red/blue team-list feeder leaf shared by TDM and Freeze.
=============
*/
static const char *CG_FeederItemTextTDMFreezeTeamList( int team, int index, int column, qhandle_t *handle ) {
	cgFeederRow_t		row;
	const cgTdmStats_t	*stats;
	int				net;

	stats = NULL;
	net = 0;

	if ( !CG_BuildFeederRow( index, team, &row ) ) {
		return "";
	}
	if ( !row.info || !row.info->infoValid || !row.scoreRow ) {
		return "";
	}

	if ( row.scoreIndex >= 0 && row.scoreIndex < MAX_CLIENTS ) {
		stats = &cg.tdmStats[row.scoreIndex];
	}

	if ( column <= 5 ) {
		return CG_FeederItemTextTeamListLeadColumns( &row, column, handle );
	}

	switch ( column ) {
	case 6:
		return va( "%i", row.scoreRow->score );
	case 7:
		if ( cgs.gametype == GT_FREEZE ) {
			return va( "%i/%i", row.scoreRow->kills, row.scoreRow->deaths );
		}
		if ( stats && stats->valid ) {
			net = row.scoreRow->kills + stats->values[8] - stats->values[9] - stats->values[10];
		} else {
			net = row.scoreRow->kills - row.scoreRow->deaths;
		}
		return va( "%i", net );
	case 8:
		if ( cgs.gametype == GT_FREEZE ) {
			return va( "%i%%", row.scoreRow->accuracy );
		}
		return va( "%i", row.scoreRow->damage );
	case 9:
		if ( cgs.gametype == GT_FREEZE ) {
			return row.scoreRow->activePlayer ? "*" : "";
		}
		return va( "%i%%", row.scoreRow->accuracy );
	}

	return "";
}

/*
=============
CG_FeederItemTextTDMFreezeStats

Formats the retail rich team-stats rows shared by TDM and Freeze end-score
menus.
=============
*/
static const char *CG_FeederItemTextTDMFreezeStats( int team, int index, int column, qhandle_t *handle ) {
	cgFeederRow_t		row;
	const cgTdmStats_t	*stats;
	int			kills;
	int			net;

	(void)handle;

	if ( !CG_BuildFeederRow( index, team, &row ) ) {
		return "";
	}
	if ( !row.info || !row.info->infoValid || !row.scoreRow ||
		 row.scoreIndex < 0 || row.scoreIndex >= MAX_CLIENTS ) {
		return "";
	}

	stats = &cg.tdmStats[row.scoreIndex];
	if ( !stats->valid ) {
		return "";
	}

	kills = row.scoreRow->kills;
	net = kills + stats->values[8] - stats->values[9] - stats->values[10];

	switch ( column ) {
	case 0:
		return row.info->name;
	case 1:
		return va( "%i", row.scoreRow->score );
	case 2:
		return va( "%i", kills );
	case 3:
		return va( "%i", row.scoreRow->deaths );
	case 4:
		return va( "%i", stats->values[10] );
	case 5:
		return va( "%i", stats->values[9] );
	case 6:
		return va( "%i", stats->values[8] );
	case 7:
		return va( "%i", net );
	case 8:
		return va( "%i", stats->values[7] );
	case 9:
		return va( "%i", stats->values[6] );
	case 10:
		return va( "%i%%", row.scoreRow->accuracy );
	case 11:
		return va( "%i", stats->values[5] );
	case 12:
		return va( "%i", stats->values[4] );
	case 13:
		return va( "%i", stats->values[3] );
	case 14:
		return va( "%i", stats->values[2] );
	case 15:
		return va( "%i", stats->values[1] );
	case 16:
		return va( "%i", stats->values[0] );
	case 17:
		return va( "%4i", row.scoreRow->time );
	}

	return "";
}

/*
=============
CG_FeederItemTextClanArenaStats

Formats the retail Clan Arena end-score kill/accuracy feeder rows.
=============
*/
static const char *CG_FeederItemTextClanArenaStats( int team, int index, int column, qhandle_t *handle ) {
	cgFeederRow_t			row;
	const cgClanArenaStats_t	*stats;

	(void)handle;

	if ( !CG_BuildFeederRow( index, team, &row ) ) {
		return "";
	}
	if ( !row.info || !row.info->infoValid || !row.scoreRow ||
		 row.scoreIndex < 0 || row.scoreIndex >= MAX_CLIENTS ) {
		return "";
	}

	stats = &cg.clanArenaStats[row.scoreIndex];
	if ( !stats->valid ) {
		return "";
	}

	switch ( column ) {
	case 0:
		return row.info->name;
	case 1:
		return va( "%i", row.scoreRow->score );
	case 2:
		return va( "%i", row.scoreRow->kills );
	case 3:
		return va( "%i", row.scoreRow->deaths );
	case 4:
		return va( "%i", stats->damageGiven );
	case 5:
		return va( "%i", stats->damageReceived );
	case 6:
		return va( "%i%%", row.scoreRow->accuracy );
	case 7:
		return va( "%i", stats->weaponFrags[WP_GAUNTLET] );
	case 8:
		return va( "^3%i ^7%i%%", stats->weaponFrags[WP_MACHINEGUN], stats->weaponAccuracy[WP_MACHINEGUN] );
	case 9:
		return va( "^3%i ^7%i%%", stats->weaponFrags[WP_SHOTGUN], stats->weaponAccuracy[WP_SHOTGUN] );
	case 10:
		return va( "^3%i ^7%i%%", stats->weaponFrags[WP_GRENADE_LAUNCHER], stats->weaponAccuracy[WP_GRENADE_LAUNCHER] );
	case 11:
		return va( "^3%i ^7%i%%", stats->weaponFrags[WP_ROCKET_LAUNCHER], stats->weaponAccuracy[WP_ROCKET_LAUNCHER] );
	case 12:
		return va( "^3%i ^7%i%%", stats->weaponFrags[WP_LIGHTNING], stats->weaponAccuracy[WP_LIGHTNING] );
	case 13:
		return va( "^3%i ^7%i%%", stats->weaponFrags[WP_RAILGUN], stats->weaponAccuracy[WP_RAILGUN] );
	case 14:
		return va( "^3%i ^7%i%%", stats->weaponFrags[WP_PLASMAGUN], stats->weaponAccuracy[WP_PLASMAGUN] );
	case 15:
		return va( "^3%i ^7%i%%", stats->weaponFrags[WP_HEAVY_MACHINEGUN], stats->weaponAccuracy[WP_HEAVY_MACHINEGUN] );
	case 16:
		return va( "%4i", row.scoreRow->time );
	}

	return "";
}

/*
=============
CG_FeederItemTextCTFFamilyStats

Formats the retail shared CTF-family end-score feeder rows used by the CTF,
1FCTF, Harvester, Domination, and Attack & Defend menus.
=============
*/
static const char *CG_FeederItemTextCTFFamilyStats( int team, int index, int column, qhandle_t *handle ) {
	cgFeederRow_t		row;
	const cgCtfStats_t	*stats;
	int			net;

	(void)handle;

	if ( !CG_BuildFeederRow( index, team, &row ) ) {
		return "";
	}
	if ( !row.info || !row.info->infoValid || !row.scoreRow ||
		 row.scoreIndex < 0 || row.scoreIndex >= MAX_CLIENTS ) {
		return "";
	}

	stats = &cg.ctfStats[row.scoreIndex];
	if ( !stats->valid ) {
		return "";
	}

	net = row.scoreRow->kills - row.scoreRow->deaths - stats->values[11];

	switch ( column ) {
	case 0:
		return row.info->name;
	case 1:
		return va( "%i", row.scoreRow->score );
	case 2:
		return va( "%i", row.scoreRow->kills );
	case 3:
		return va( "%i", row.scoreRow->deaths );
	case 4:
		return va( "%i", stats->values[11] );
	case 5:
		return va( "%i", net );
	case 6:
		return va( "%i", stats->values[10] );
	case 7:
		return va( "%i", stats->values[9] );
	case 8:
		return va( "%i%%", row.scoreRow->accuracy );
	case 9:
		return va( "%i", stats->values[8] );
	case 10:
		return va( "%i", stats->values[7] );
	case 11:
		return va( "%i", stats->values[6] );
	case 12:
		return va( "%i", stats->values[5] );
	case 13:
		return va( "%i", stats->values[4] );
	case 14:
		return va( "%i", stats->values[3] );
	case 15:
		return va( "%i", stats->values[2] );
	case 16:
		return va( "%i", stats->values[1] );
	case 17:
		return va( "%i", stats->values[0] );
	case 18:
		return va( "%4i", row.scoreRow->time );
	}

	return "";
}

/*
=============
CG_FeederItemText

Dispatches the retail scoreboard, team-list, and team-stats feeders to the
reconstructed leaf helpers.
=============
*/
static const char *CG_FeederItemText( float feederID, int index, int column, qhandle_t *handle ) {
	int		team;

	*handle = -1;
	team = CG_GetFeederTeam( feederID );

	if ( CG_IsTeamStatsFeeder( feederID ) ) {
		switch ( cgs.gametype ) {
		case GT_TEAM:
		case GT_FREEZE:
			return CG_FeederItemTextTDMFreezeStats( team, index, column, handle );
		case GT_CLAN_ARENA:
			return CG_FeederItemTextClanArenaStats( team, index, column, handle );
		case GT_CTF:
		case GT_1FCTF:
		case GT_HARVESTER:
		case GT_DOMINATION:
		case GT_ATTACK_DEFEND:
			return CG_FeederItemTextCTFFamilyStats( team, index, column, handle );
		default:
			return "";
		}
	}

	if ( CG_IsTeamListFeeder( feederID ) ) {
		switch ( cgs.gametype ) {
		case GT_TEAM:
		case GT_FREEZE:
			return CG_FeederItemTextTDMFreezeTeamList( team, index, column, handle );
		case GT_CLAN_ARENA:
			return CG_FeederItemTextClanArenaTeamList( team, index, column, handle );
		case GT_CTF:
		case GT_1FCTF:
		case GT_HARVESTER:
		case GT_DOMINATION:
		case GT_ATTACK_DEFEND:
			return CG_FeederItemTextCTFFamilyTeamList( team, index, column, handle );
		default:
			return CG_FeederItemTextFallbackTeamList( team, index, column, handle );
		}
	}

	if ( cgs.gametype == GT_RACE ) {
		return CG_FeederItemTextRaceScoreboard( index, column, handle );
	}
	return CG_FeederItemTextScoreboard( index, column, handle );
}


/*
=============
CG_FeederItemImage

Retail keeps the cgDC.feederItemImage callback as a null stub and sources the
scoreboard icons through the feeder-text handle out-param instead.
=============
*/
static qhandle_t CG_FeederItemImage( float feederID, int index ) {
	(void)feederID;
	(void)index;

	return 0;
}

/*
=============
CG_FeederSelection

Maintains the selected scoreboard row and mirrors the retail team-list cursor
selection into the cached live/end scoreboard menus.
=============
*/
static void CG_FeederSelection( float feederID, int index, const char *cvar ) {
	int		selectedIndex;
	int		selectedScoreIndex;
	team_t	team;

	(void)cvar;

	if ( index == -1 ) {
		return;
	}

	if ( cgs.gametype < GT_TEAM || ( !CG_IsTeamListFeeder( feederID ) && !CG_IsTeamStatsFeeder( feederID ) ) ) {
		cg.selectedScore = index;
		return;
	}

	team = ( feederID == FEEDER_REDTEAM_LIST || feederID == FEEDER_REDTEAM_STATS ) ? TEAM_RED : TEAM_BLUE;
	selectedScoreIndex = CG_ScoreIndexFromTeamRow( index, team );
	if ( selectedScoreIndex < 0 ) {
		return;
	}

	cg.selectedScore = selectedScoreIndex;
	selectedIndex = CG_TeamRowFromScoreIndex( cg.selectedScore, team );
	if ( selectedIndex < 0 ) {
		selectedIndex = index;
	}

	if ( !cgScoreboardSelectionMenus[0] && !cgScoreboardSelectionMenus[1] ) {
		CG_CacheScoreboardSelectionMenus();
	}

	CG_SyncScoreboardTeamListSelection( team, selectedIndex );
}

/*
=============
CG_Cvar_Get

Provides the retail cgDC numeric cvar callback.
=============
*/
static float CG_Cvar_Get( const char *cvar ) {
	char buff[128];

	memset( buff, 0, sizeof( buff ) );
	trap_Cvar_VariableStringBuffer( cvar, buff, sizeof( buff ) );
	return atof( buff );
}

/*
=============
CG_Cvar_GetString

Provides the named retail cgDC string callback wrapper.
=============
*/
void CG_Cvar_GetString( const char *cvar, char *buffer, int bufsize ) {
	if ( !buffer || bufsize <= 0 ) {
		return;
	}

	buffer[0] = '\0';

	if ( !cvar || !cvar[0] ) {
		return;
	}

	trap_Cvar_VariableStringBuffer( cvar, buffer, bufsize );
}

/*
=============
CG_UseMatchSummaryChatLayout

Retail switches the native chat field into the narrower summary layout only
during intermission.
=============
*/
static qboolean CG_UseMatchSummaryChatLayout( void ) {
	if ( cg.snap && cg.snap->ps.pm_type == PM_INTERMISSION ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_GetPhysicsTime

Mirrors the retail native getter used by timestamped chat and notify paths.
=============
*/
static int CG_GetPhysicsTime( void ) {
	return cg.physicsTime;
}

/*
=============
CG_GetChatFieldY

Returns the retail 640-space Y origin for the live chat input field.
=============
*/
static float CG_GetChatFieldY( void ) {
	return CG_UseMatchSummaryChatLayout() ? 455.0f : 413.0f;
}

/*
=============
CG_GetChatFieldPixelWidth

Returns the retail 640-space width for the live chat input field.
=============
*/
static float CG_GetChatFieldPixelWidth( void ) {
	return CG_UseMatchSummaryChatLayout() ? 300.0f : 640.0f;
}

/*
=============
CG_GetChatFieldWidthInChars

Returns the retail character width used by the live chat input field.
=============
*/
static int CG_GetChatFieldWidthInChars( void ) {
	return CG_UseMatchSummaryChatLayout() ? 30 : 73;
}

/*
=============
CG_NativeGetChatFieldY

Exports the chat-field Y position through the integer contract used by vmMain
and the recovered native cgame slot surface.
=============
*/
static int CG_NativeGetChatFieldY( void ) {
	return (int)CG_GetChatFieldY();
}

/*
=============
CG_NativeGetChatFieldPixelWidth

Exports the chat-field pixel width through the integer contract used by vmMain
and the recovered native cgame slot surface.
=============
*/
static int CG_NativeGetChatFieldPixelWidth( void ) {
	return (int)CG_GetChatFieldPixelWidth();
}

/*
=============
CG_CopyClientIdentity

Marshals the reconstructed client-identity sidecar into the caller buffer.
=============
*/
static qboolean CG_CopyClientIdentity( int clientNum, void *outIdentity ) {
	cgameClientIdentity_t	*identity;
	const clientInfo_t		*ci;
	char					cleanName[MAX_QPATH];

	if ( !outIdentity ) {
		return qfalse;
	}

	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return qfalse;
	}

	ci = &cgs.clientinfo[clientNum];
	if ( !ci->infoValid ) {
		return qfalse;
	}

	identity = (cgameClientIdentity_t *)outIdentity;
	memset( identity, 0, sizeof( *identity ) );
	identity->clientNum = clientNum;
	identity->identityTransport = 0;
	identity->identityLow = ci->identityLow;
	identity->identityHigh = ci->identityHigh;

	/*
	 * The committed retail corpus only observes this sidecar word being copied
	 * back out through the native export. The retail player parser rebuilds the
	 * Steam identity words and avatar cache, but it never materializes a
	 * separate producer for the transport discriminator, and the recovered host
	 * overlay consumer only branches on the identity words. Preserve that
	 * observed ABI by keeping the exported transport word explicitly zero.
	 */
	Q_strncpyz( identity->displayName, ci->name, sizeof( identity->displayName ) );
	Q_strncpyz( cleanName, ci->name, sizeof( cleanName ) );
	Q_CleanStr( cleanName );
	Q_strncpyz( identity->cleanName,
		cleanName[0] ? cleanName : ci->name, sizeof( identity->cleanName ) );

	return qtrue;
}

/*
=============
CG_SetClientSpeakingState

Mirrors the retail voice-indicator sidecar on top of the existing HUD state.
=============
*/
void *CG_SetClientSpeakingState( int clientNum, int speaking ) {
	clientInfo_t			*ci;
	cgClientSpeakingState_t	*speakingState;

	if ( clientNum < 0 || clientNum >= MAX_CLIENTS ) {
		return NULL;
	}

	ci = &cgs.clientinfo[clientNum];
	speakingState = &cgClientSpeakingState[clientNum];
	speakingState->speaking = speaking ? qtrue : qfalse;
	speakingState->time = cg.time;

	if ( speaking ) {
		cgs.currentVoiceClient = clientNum;
		cg.voiceTime = cg.time;
	} else if ( cgs.currentVoiceClient == clientNum ) {
		cgs.currentVoiceClient = -1;
		cg.voiceTime = 0;
	}

	return ci;
}

/*
=============
CG_NativeSetClientSpeakingState

Exports the speaking-state sidecar through the integer/pointer contract used by
vmMain and the recovered native cgame slot surface.
=============
*/
static int CG_NativeSetClientSpeakingState( int clientNum, int speaking ) {
	return (int)(intptr_t)CG_SetClientSpeakingState( clientNum, speaking );
}

/*
=============
CG_Text_PaintWithCursorExt

Mirrors the retail cgame cursor-signature wrapper by forwarding through the
shared host-text painter while honoring explicit font buckets.
=============
*/
static void CG_Text_PaintWithCursorExt( float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style, int fontIndex ) {
	(void)cursorPos;
	(void)cursor;

	CG_Text_PaintExt( x, y, scale, color, text, 0.0f, limit, style, fontIndex );
}

/*
=============
CG_Text_PaintWithCursor

Mirrors the retail cgame cursor-signature wrapper by forwarding through the
shared host-text painter.
=============
*/
void CG_Text_PaintWithCursor( float x, float y, float scale, vec4_t color, const char *text, int cursorPos, char cursor, int limit, int style ) {
	CG_Text_PaintWithCursorExt( x, y, scale, color, text, cursorPos, cursor, limit, style, ITEM_FONT_INHERIT );
}

/*
=============
CG_OwnerDrawWidth

Calculates the width to reserve for a HUD owner-draw element.
=============
*/
static int CG_OwnerDrawWidth( int ownerDraw, float scale ) {
	switch ( ownerDraw ) {
	case CG_GAME_TYPE:
		return CG_Text_Width( CG_GameTypeString(), scale, 0 );
	case CG_GAME_STATUS:
		return CG_Text_Width( CG_GetGameStatusText(), scale, 0 );
	case CG_MATCH_STATUS:
		return CG_Text_Width( CG_GetMatchStatusText(), scale, 0 );
	case CG_KILLER:
		return CG_Text_Width( CG_GetKillerText(), scale, 0 );
	default:
		break;
	}

	return 0;
}

/*
=============
CG_PlayCinematic

Starts a looping cinematic through the retail cgDC callback.
=============
*/
static int CG_PlayCinematic( const char *name, float x, float y, float w, float h ) {
	return trap_CIN_PlayCinematic( name, x, y, w, h, CIN_loop );
}

/*
=============
CG_StopCinematic

Stops a cinematic through the retail cgDC callback.
=============
*/
static void CG_StopCinematic( int handle ) {
	trap_CIN_StopCinematic( handle );
}

/*
=============
CG_DrawCinematic

Sets the cinematic extents and draws through the retail cgDC callback.
=============
*/
static void CG_DrawCinematic( int handle, float x, float y, float w, float h ) {
	trap_CIN_SetExtents( handle, x, y, w, h );
	trap_CIN_DrawCinematic( handle );
}

/*
=============
CG_RunCinematicFrame

Advances a cinematic through the retail cgDC callback.
=============
*/
static void CG_RunCinematicFrame( int handle ) {
	trap_CIN_RunCinematic( handle );
}

static const char *cgScoreTextureNames[] = {
	"ui/assets/score/1st_plyr_leads.tga",
	"ui/assets/score/1st_plyr_notready.tga",
	"ui/assets/score/1st_plyr_ready.tga",
	"ui/assets/score/1st_plyr_tied.tga",
	"ui/assets/score/1st_plyr_trails.tga",
	"ui/assets/score/2nd_plyr_leads.tga",
	"ui/assets/score/2nd_plyr_notready.tga",
	"ui/assets/score/2nd_plyr_ready.tga",
	"ui/assets/score/2nd_plyr_tied.tga",
	"ui/assets/score/2nd_plyr_trails.tga",
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
	"ui/assets/menu/centerbg_fade.tga",
	"ui/assets/hud/scoreboxl2.tga",
	"ui/assets/hud/scoreboxm.tga",
	"ui/assets/hud/scoreboxr.tga",
	"ui/assets/hud/rteambgl.tga",
	"ui/assets/hud/rteambgr.tga",
	"ui/assets/hud/bteambgl.tga",
	"ui/assets/hud/bteambgr.tga",
	"ui/assets/hud/health.tga",
	"ui/assets/hud/armor.tga",
	"ui/assets/hud/flag",
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
#define CG_COUNTRY_FILE_BUFFER 4096

/*
=============
CG_IsCountryCodeToken

Validates a country token before it is used in a shader path.
=============
*/
static qboolean CG_IsCountryCodeToken( const char *countryCode ) {
	int		i;
	char	c;

	if ( !countryCode || !countryCode[0] ) {
		return qfalse;
	}

	for ( i = 0; ( c = countryCode[i] ) != '\0'; i++ ) {
		if ( i >= MAX_COUNTRY_CODE - 1 ) {
			return qfalse;
		}

		if ( ( c >= 'a' && c <= 'z' ) || ( c >= 'A' && c <= 'Z' ) ||
			( c >= '0' && c <= '9' ) || c == '_' || c == '-' ) {
			continue;
		}

		return qfalse;
	}

	return qtrue;
}

/*
=============
CG_RegisterCountryFlag

Registers a country flag shader with the retail none-flag fallback.
=============
*/
qhandle_t CG_RegisterCountryFlag( const char *countryCode ) {
	char		normalized[MAX_COUNTRY_CODE];
	char		filename[MAX_QPATH];
	qhandle_t	shader;

	if ( !cgs.media.countryFlagNoneShader ) {
		cgs.media.countryFlagNoneShader = trap_R_RegisterShaderNoMip( "ui/assets/flags/none.tga" );
	}

	if ( !CG_IsCountryCodeToken( countryCode ) ) {
		return cgs.media.countryFlagNoneShader;
	}

	Q_strncpyz( normalized, countryCode, sizeof( normalized ) );
	Q_strlwr( normalized );
	Com_sprintf( filename, sizeof( filename ), "ui/assets/flags/%s.tga", normalized );

	shader = trap_R_RegisterShaderNoMip( filename );
	if ( !shader ) {
		return cgs.media.countryFlagNoneShader;
	}

	return shader;
}

/*
=============
CG_CacheCountryFlags

Pre-registers the retail country-flag shader bank used by scoreboard widgets.
=============
*/
static void CG_CacheCountryFlags( void ) {
	static const char	filename[] = "ui/country.txt";
	fileHandle_t		f;
	int			len;
	char			buffer[CG_COUNTRY_FILE_BUFFER];
	char			*text_p;
	char			*token;

	cgs.media.countryFlagNoneShader = trap_R_RegisterShaderNoMip( "ui/assets/flags/none.tga" );

	len = trap_FS_FOpenFile( filename, &f, FS_READ );
	if ( len <= 0 ) {
		CG_Printf( "ERROR: CG_CacheCountryFlags: %s too small\n", filename );
		return;
	}

	if ( len >= sizeof( buffer ) ) {
		CG_Printf( "ERROR: CG_CacheCountryFlags: %s too large. Size is %d, limit is %d\n",
			filename, len, (int)( sizeof( buffer ) - 1 ) );
		trap_FS_FCloseFile( f );
		return;
	}

	trap_FS_Read( buffer, len, f );
	buffer[len] = '\0';
	trap_FS_FCloseFile( f );

	text_p = buffer;
	while ( 1 ) {
		token = COM_Parse( &text_p );
		if ( !token || !token[0] ) {
			break;
		}

		CG_RegisterCountryFlag( token );
	}
}

/*
=============
CG_LoadHudScriptBuffer

Reads the active HUD script include list into a temporary buffer for feature
scans performed during HUD bootstrap.
=============
*/
static qboolean CG_LoadHudScriptBuffer( const char *hudSet, char *buffer, int bufferSize ) {
	fileHandle_t	f;
	int			len;

	if ( !hudSet || !hudSet[0] || !buffer || bufferSize <= 0 ) {
		return qfalse;
	}

	len = trap_FS_FOpenFile( hudSet, &f, FS_READ );
	if ( len <= 0 ) {
		return qfalse;
	}

	if ( len >= bufferSize ) {
		len = bufferSize - 1;
	}

	trap_FS_Read( buffer, len, f );
	buffer[len] = '\0';
	trap_FS_FCloseFile( f );
	return qtrue;
}

/*
=============
CG_HudScriptHasMenuLoads

Reports whether the selected HUD script contains menu include directives so the
menu-driven HUD paint path should be considered active.
=============
*/
static qboolean CG_HudScriptHasMenuLoads( const char *hudSet ) {
	char	buffer[CG_HUD_SCRIPT_BUFFER];

	if ( !CG_LoadHudScriptBuffer( hudSet, buffer, sizeof( buffer ) ) ) {
		return qfalse;
	}

	return ( strstr( buffer, "loadMenu" ) != NULL ) ? qtrue : qfalse;
}

/*
=============
CG_HudScriptHasCompetitiveMenus

Scans the hud script for Quake Live competitive HUD menu references.
=============
*/
static qboolean CG_HudScriptHasCompetitiveMenus( const char *hudSet ) {
	char		buffer[CG_HUD_SCRIPT_BUFFER];

	if ( !CG_LoadHudScriptBuffer( hudSet, buffer, sizeof( buffer ) ) ) {
		return qfalse;
	}

	if ( strstr( buffer, "comp_hud" ) || strstr( buffer, "comp_spectator" ) ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
CG_InitDisplayContext

Matches the retail cgDC bootstrap helper recovered from the native cgame init path.
=============
*/
static void CG_InitDisplayContext( void ) {
	cgDC.registerShaderNoMip = &trap_R_RegisterShaderNoMip;
	cgDC.setColor = &trap_R_SetColor;
	cgDC.drawHandlePic = &CG_DrawPic;
	cgDC.drawStretchPic = &trap_R_DrawStretchPic;
	cgDC.drawText = &CG_Text_Paint;
	cgDC.drawTextExt = &CG_Text_PaintExt;
	cgDC.textWidth = &CG_Text_Width;
	cgDC.textWidthExt = &CG_Text_WidthExt;
	cgDC.textHeight = &CG_Text_Height;
	cgDC.textHeightExt = &CG_Text_HeightExt;
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
	cgDC.getCVarString = &CG_Cvar_GetString;
	cgDC.getCVarValue = CG_Cvar_Get;
	cgDC.drawTextWithCursor = &CG_Text_PaintWithCursor;
	cgDC.drawTextWithCursorExt = &CG_Text_PaintWithCursorExt;
	cgDC.setOverstrikeMode = &trap_Key_SetOverstrikeMode;
	cgDC.getOverstrikeMode = &trap_Key_GetOverstrikeMode;
	cgDC.startLocalSound = &trap_S_StartLocalSound;
	cgDC.ownerDrawHandleKey = &CG_OwnerDrawHandleKey;
	cgDC.feederCount = &CG_FeederCount;
	cgDC.feederItemImage = &CG_FeederItemImage;
	cgDC.feederItemText = &CG_FeederItemText;
	cgDC.feederSelection = &CG_FeederSelection;
	cgDC.setBinding = &trap_Key_SetBinding;
	cgDC.getBindingBuf = &trap_Key_GetBindingBuf;
	cgDC.keynumToStringBuf = &trap_Key_KeynumToStringBuf;
	cgDC.executeText = &trap_Cmd_ExecuteText;
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
	cgDC.adjustFrom640 = &CG_AdjustFrom640;
	cgDC.setAdjustFrom640Mode = &CG_SetAdjustFrom640Mode;
	cgDC.glconfig = cgs.glconfig;
	cgDC.xscale = cgs.screenXScale;
	cgDC.yscale = cgs.screenYScale;
	cgDC.bias = cgs.screenXBias;

	Init_Display( &cgDC );
}

/*
=============
CG_RegisterHudFonts

Matches the retail HUD font bootstrap that runs immediately after display-context init.
=============
*/
static void CG_RegisterHudFonts( void ) {
	if ( cgDC.Assets.fontRegistered ) {
		return;
	}

	trap_R_RegisterFont( QL_FONT_NAME_TEXT, QL_FONT_TEXT_POINT_SIZE, &cgDC.Assets.textFont );
	trap_R_RegisterFont( QL_FONT_NAME_SMALL, QL_FONT_SMALL_POINT_SIZE, &cgDC.Assets.smallFont );
	trap_R_RegisterFont( QL_FONT_NAME_BIG, QL_FONT_BIG_POINT_SIZE, &cgDC.Assets.bigFont );
	cgDC.Assets.fontRegistered = qtrue;
}

/*
=============
CG_LoadHudMenu

Loads the configured HUD menu set and refreshes retail scoreboard menu caches.
=============
*/
void CG_LoadHudMenu( void ) {
	char buff[1024];
	const char *hudSet;

	trap_Cvar_VariableStringBuffer( "cg_hudFiles", buff, sizeof( buff ) );
	hudSet = buff;
	if ( hudSet[0] == '\0' ) {
		hudSet = CG_DEFAULT_HUD_FILE;
	}

	cg.hudMenusLoaded = CG_HudScriptHasMenuLoads( hudSet );
	cg.competitiveHudLoaded = CG_HudScriptHasCompetitiveMenus( hudSet );
	CG_LoadMenus( hudSet );
	CG_CacheDraw2DMenuCache();
	CG_CacheScoreboardSelectionMenus();
}


/*
=============
CG_AssetCache

Registers the shared UI art cache used by the client game module.
=============
*/
void CG_AssetCache( void ) {
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
Rebuilds the cgame runtime and performs callbacks to make the loading info screen update.
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
	memset( cgClientSpeakingState, 0, sizeof( cgClientSpeakingState ) );
  
	CG_ClearAutomationState();
	CG_ResetIntermissionLetterboxState();
	cg.spectatorPrimaryClient = -1;
	cg.spectatorSecondaryClient = -1;
	cg.spectatorFollowClient = -1;
	cg.spectatorTrackedClient = -1;
	cg.trackedPlayerClientNum = -1;
	cg.trackedPlayerPriority = CG_SPECTATOR_TRACK_NONE;
	cg.trackedPlayerExpireTime = 0;
	cg.pendingFollowKillerClient = -1;
	cg.pendingFollowKillerTime = 0;
	cg.viewFilter.count = 0;
	cg.viewFilter.index = 0;
	cg.viewFilter.lastYaw = 0.0f;
	cg.viewFilter.lastPitch = 0.0f;
	CG_ClearSpectatorItemPickups();
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

	CG_SetWeaponSelect( WP_MACHINEGUN );

	cgs.redflag = cgs.blueflag = -1; // For compatibily, default to unset for
	cgs.flagStatus = -1;
	// old servers

	// get the rendering configuration from the client system
	trap_GetGlconfig( &cgs.glconfig );
	cgs.screenXScale = cgs.glconfig.vidWidth / 640.0;
	cgs.screenYScale = cgs.glconfig.vidHeight / 480.0;
	if ( cgs.glconfig.vidWidth * SCREEN_HEIGHT > cgs.glconfig.vidHeight * SCREEN_WIDTH ) {
		cgs.screenXBias = 0.5f * ( (float)cgs.glconfig.vidWidth - ( (float)cgs.glconfig.vidHeight * ( (float)SCREEN_WIDTH / (float)SCREEN_HEIGHT ) ) );
	} else {
		cgs.screenXBias = 0.0f;
	}

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
	CG_CacheCountryFlags();

	CG_InitDisplayContext();
	CG_RegisterHudFonts();
	CG_ResetLoadingState();

	// load the new map
	CG_LoadingString( "collision map" );

	trap_CM_LoadMap( cgs.mapname );

	CG_InitBrowserRuntime();
	CG_AdvanceLoadingProgress();

	cg.loading = qtrue;		// force players to load instead of defer

	CG_LoadingString( "sounds" );

	CG_RegisterSounds();
	CG_AdvanceLoadingProgress();

	CG_LoadingString( "graphics" );

	CG_RegisterGraphics();
	CG_AdvanceLoadingProgress();

	CG_LoadingString( "clients" );

	CG_RegisterClients();		// if low on memory, some clients will be deferred

	CG_AssetCache();
	CG_LoadHudMenu();      // load new hud stuff

	cg.loading = qfalse;	// future players will be deferred

	CG_InitLocalEntities();
	CG_ClearQueuedWorldMarkers();

	CG_InitMarkPolys();

	// remove the last loading update
	cg.infoScreenText[0] = 0;

	// Make sure we have update values (scores)
	CG_SetConfigValues();

	CG_StartMusic();

	CG_AdvanceLoadingProgress();
	CG_LoadingString( "" );

	CG_InitTeamChat();
	CG_ReplayLastMessageFromCvar();

	CG_ShaderStateChanged();
	trap_AdvertisementBridge_InitCGame();

	trap_S_ClearLoopingSounds( qtrue );
}

/*
=================
CG_Shutdown

Called before every level change or subsystem restart and tears down host-side cgame bridges.
=================
*/
void CG_Shutdown( void ) {
	// some mods may need to do cleanup work here,
	// like closing files or archiving session data
	CG_ClearAutomationState();
	memset( cgClientSpeakingState, 0, sizeof( cgClientSpeakingState ) );
	trap_AdvertisementBridge_ShutdownCGame();
	trap_Cvar_Set( "ui_mainmenu", "1" );
}


/*
==================
CG_EventHandling
==================
 type 0 - no event handling
      1 - team menu
      2 - hud editor

*/
