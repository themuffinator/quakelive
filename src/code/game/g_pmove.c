#include <stdarg.h>
#include "g_local.h"

// Retail qagame stores these high-bit groups in the pmove cvar table slab at
// 0x1008f7c4..0x1008fb20; names below describe the observed grouping.
#define PMOVE_CVAR_FLAG_FACTORY_MANAGED	0x00100000
#define PMOVE_CVAR_FLAG_CHANGE_LATCH	0x00004000
#define PMOVE_CVAR_FLAG_CUSTOM_SETTING	0x00040000

#define PMOVE_CVAR_FLAGS_FACTORY_ONLY	PMOVE_CVAR_FLAG_FACTORY_MANAGED
#define PMOVE_CVAR_FLAGS_FACTORY		(PMOVE_CVAR_FLAG_FACTORY_MANAGED | PMOVE_CVAR_FLAG_CHANGE_LATCH)
#define PMOVE_CVAR_FLAGS_CUSTOM		(PMOVE_CVAR_FLAG_FACTORY_MANAGED | PMOVE_CVAR_FLAG_CUSTOM_SETTING)
#define PMOVE_CVAR_FLAGS_CUSTOM_LATCH	(PMOVE_CVAR_FLAG_FACTORY_MANAGED | PMOVE_CVAR_FLAG_CHANGE_LATCH | PMOVE_CVAR_FLAG_CUSTOM_SETTING)

#define PMOVE_RETAIL_MIN_POSITIVE	0.001f

static vmCvar_t g_pmove_airAccel_cvar;
static vmCvar_t g_pmove_airControl_cvar;
static vmCvar_t g_pmove_airStepFriction_cvar;
static vmCvar_t g_pmove_airSteps_cvar;
static vmCvar_t g_pmove_airStopAccel_cvar;
static vmCvar_t g_pmove_autoHop_cvar;
static vmCvar_t g_pmove_bunnyHop_cvar;
static vmCvar_t g_pmove_chainJump_cvar;
static vmCvar_t g_pmove_chainJumpVelocity_cvar;
static vmCvar_t g_pmove_circleStrafeFriction_cvar;
static vmCvar_t g_pmove_crouchSlide_cvar;
static vmCvar_t g_pmove_crouchSlideFriction_cvar;
static vmCvar_t g_pmove_crouchSlideTime_cvar;
static vmCvar_t g_pmove_crouchStepJump_cvar;
static vmCvar_t g_pmove_doubleJump_cvar;
static vmCvar_t g_pmove_jumpTimeDeltaMin_cvar;
static vmCvar_t g_pmove_jumpVelocity_cvar;
static vmCvar_t g_pmove_jumpVelocityMax_cvar;
static vmCvar_t g_pmove_jumpVelocityScaleAdd_cvar;
static vmCvar_t g_pmove_jumpVelocityTimeThreshold_cvar;
static vmCvar_t g_pmove_jumpVelocityTimeThresholdOffset_cvar;
static vmCvar_t g_pmove_noPlayerClip_cvar;
static vmCvar_t g_pmove_rampJump_cvar;
static vmCvar_t g_pmove_rampJumpScale_cvar;
static vmCvar_t g_pmove_stepHeight_cvar;
static vmCvar_t g_pmove_stepJump_cvar;
static vmCvar_t g_pmove_stepJumpVelocity_cvar;
static vmCvar_t g_pmove_strafeAccel_cvar;
static vmCvar_t g_pmove_velocityGh_cvar;
static vmCvar_t g_pmove_walkAccel_cvar;
static vmCvar_t g_pmove_walkFriction_cvar;
static vmCvar_t g_pmove_waterSwimScale_cvar;
static vmCvar_t g_pmove_waterWadeScale_cvar;
static vmCvar_t g_pmove_weaponDropTime_cvar;
static vmCvar_t g_pmove_weaponRaiseTime_cvar;
static vmCvar_t g_pmove_wishSpeed_cvar;

static int g_pmove_last_frame = -1;
static qboolean g_pmove_force_update = qtrue;

static char s_pmoveSettingsPayload[MAX_INFO_STRING];

/*
=============
G_PmoveAppendPayload

Appends formatted text to the pmove payload buffer.
=============
*/
static qboolean G_PmoveAppendPayload( char *buffer, size_t bufferSize, size_t *length, const char *fmt, ... ) {
	va_list args;
	int written;

	if ( !buffer || !length || !fmt || bufferSize == 0 ) {
		return qfalse;
	}

	va_start( args, fmt );
	written = Q_vsnprintf( buffer + *length, bufferSize - *length, fmt, args );
	va_end( args );

	if ( written < 0 || ( size_t )written >= ( bufferSize - *length ) ) {
		return qfalse;
	}

	*length += written;
	return qtrue;
}

/*
=============
G_PmoveSerializeSettings

Encodes the active pmove settings into the retail compact token stream for
configstring broadcasts.
=============
*/
static qboolean G_PmoveSerializeSettings( const pmove_settings_t *settings, char *buffer, size_t bufferSize ) {
	size_t length = 0;

	if ( !settings || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';

	if ( !G_PmoveAppendPayload(
		buffer,
		bufferSize,
		&length,
		"%.6f %.6f %i %.6f %i %i %i %i %.6f %.6f %i %i %.6f %.6f %.6f %.6f %.6f %.6f %i %i %.6f %.6f %i %.6f %.6f %.6f %.6f %.6f %.6f %.6f %i %i %.6f",
		settings->airAccel,
		settings->airStepFriction,
		settings->airSteps,
		settings->airStopAccel,
		settings->autoHop ? 1 : 0,
		settings->bunnyHop ? 1 : 0,
		settings->chainJump,
		(int)settings->chainJumpVelocity,
		settings->circleStrafeFriction,
		settings->crouchSlideFriction,
		settings->crouchSlideTime,
		settings->crouchStepJump ? 1 : 0,
		settings->jumpTimeDeltaMin,
		settings->jumpVelocity,
		settings->jumpVelocityMax,
		settings->jumpVelocityScaleAdd,
		settings->jumpVelocityTimeThreshold,
		settings->jumpVelocityTimeThresholdOffset,
		settings->noPlayerClip ? 1 : 0,
		settings->rampJump ? 1 : 0,
		settings->rampJumpScale,
		settings->stepHeight,
		settings->stepJump ? 1 : 0,
		settings->stepJumpVelocity,
		settings->strafeAccel,
		settings->velocityGh,
		settings->walkAccel,
		settings->walkFriction,
		settings->waterSwimScale,
		settings->waterWadeScale,
		settings->weaponDropTime,
		settings->weaponRaiseTime,
		settings->wishSpeed
	) ) {
		return qfalse;
	}

	// Retail cgame consumes only the first 33 tokens. The trailing extension keeps
	// reconstruction-only prediction knobs available to the current source cgame.
	if ( !G_PmoveAppendPayload(
		buffer,
		bufferSize,
		&length,
		" %.6f %i %i %.6f %.6f %i %i %i %.6f %i %i %i %i %i",
		settings->airControl,
		settings->crouchSlide ? 1 : 0,
		settings->doubleJump ? 1 : 0,
		settings->machinegunIronsightsScale,
		settings->gauntletSpeedFactor,
		settings->midAirMinimumHeight,
		settings->nailgunBounceEnabled ? 1 : 0,
		settings->nailgunBouncePercentage,
		settings->quadDamageMultiplier,
		settings->guidedRocketEnabled ? 1 : 0,
		settings->quadHogEnabled,
		settings->quadHogIdleSeconds,
		settings->quadHogTimeSeconds,
		settings->quadHogPingRateSeconds
	) ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
G_PmovePublishSettings

Updates the pmove settings configstring when the payload changes.
=============
*/
static void G_PmovePublishSettings( qboolean forceBroadcast ) {
	char payload[MAX_INFO_STRING];
	qboolean encoded;

	encoded = G_PmoveSerializeSettings( &g_pmoveSettings, payload, sizeof( payload ) );
	if ( !encoded ) {
		payload[0] = '\0';
	}

	if ( !forceBroadcast && !Q_stricmp( payload, s_pmoveSettingsPayload ) ) {
		return;
	}

	trap_SetConfigstring( CS_PMOVE_SETTINGS, payload );
	Q_strncpyz( s_pmoveSettingsPayload, payload, sizeof( s_pmoveSettingsPayload ) );
}

/*
=============
G_PmoveClearConfigstring

Resets the pmove settings configstring payload cache and clears the broadcast state.
=============
*/
void G_PmoveClearConfigstring( void ) {
	s_pmoveSettingsPayload[0] = '\0';
	trap_SetConfigstring( CS_PMOVE_SETTINGS, "" );
}

pmove_settings_t g_pmoveSettings;
static int g_pmoveWeaponReloadOverrides[WP_NUM_WEAPONS];

/*
=============
G_PmoveApplyProfileFlags

Seeds the retail movement-profile flags into a freshly spawned playerstate.
=============
*/
void G_PmoveApplyProfileFlags( playerState_t *ps ) {
	if ( !ps ) {
		return;
	}

	ps->pm_flags &= ~( PMF_CROUCH_SLIDE | PMF_DOUBLE_JUMP | PMF_AIR_CONTROL );

	if ( g_pmoveSettings.crouchSlide ) {
		ps->pm_flags |= PMF_CROUCH_SLIDE;
	}
	if ( g_pmoveSettings.doubleJump ) {
		ps->pm_flags |= PMF_DOUBLE_JUMP;
	}
	if ( g_pmoveSettings.airControl > 0.0f ) {
		ps->pm_flags |= PMF_AIR_CONTROL;
	}

	if ( !( ps->pm_flags & PMF_CROUCH_SLIDE ) ) {
		ps->crouchSlideTime = 0;
	}
}

/*
=============
G_PmoveRegisterCvar

Registers a pmove tuning cvar with the VM bridge.
=============
*/
static void G_PmoveRegisterCvar( vmCvar_t *vmCvar, const char *name, const char *defaultValue, int flags ) {
	trap_Cvar_Register( vmCvar, name, defaultValue, flags );
}

/*
=============
G_PmoveClampRetailMinPositive

Applies the retail pmove lower bound used by the qagame callback cache.
=============
*/
static float G_PmoveClampRetailMinPositive( float value ) {
	return ( value >= PMOVE_RETAIL_MIN_POSITIVE ) ? value : PMOVE_RETAIL_MIN_POSITIVE;
}

/*
=============
G_PmoveUpdateCvar

Synchronizes a pmove tuning cvar mirror and runs the retail change callback
side effect for callback-backed pmove entries.
=============
*/
static void G_PmoveUpdateCvar( vmCvar_t *vmCvar, const char *name, qboolean trackChange ) {
	int	modificationCount;

	if ( !vmCvar ) {
		return;
	}

	modificationCount = vmCvar->modificationCount;
	trap_Cvar_Update( vmCvar );

	if ( !trackChange || vmCvar->modificationCount == modificationCount ) {
		return;
	}

	if ( g_cheats.integer != 0 ) {
		trap_SendServerCommand( -1, va( "print \"Server: %s changed to %s\n\"", name, vmCvar->string ) );
	}
}

/*
=============
G_PmoveDefaultWeaponReloadTime

Provides the compiled reload fallback for a specific weapon slot.
=============
*/
static int G_PmoveDefaultWeaponReloadTime( weapon_t weapon ) {
	const pmove_settings_t	*defaults;

	if ( weapon < WP_NONE || weapon >= WP_NUM_WEAPONS ) {
		return 0;
	}

	defaults = PM_GetDefaultSettings();
	if ( !defaults ) {
		return 0;
	}

	return defaults->weaponReloadTimes[weapon];
}

/*
=============
G_PmoveCacheSettings

Copies the latched pmove cvar values into the live movement settings.
=============
*/
static void G_PmoveCacheSettings( void ) {
	const pmove_settings_t	*defaults;

	defaults = PM_GetDefaultSettings();
	g_pmoveSettings.airAccel = g_pmove_airAccel_cvar.value;
	g_pmoveSettings.airControl = g_pmove_airControl_cvar.value;
	g_pmoveSettings.airStepFriction = g_pmove_airStepFriction_cvar.value;
	g_pmoveSettings.airSteps = g_pmove_airSteps_cvar.integer;
	g_pmoveSettings.airStopAccel = g_pmove_airStopAccel_cvar.value;
	g_pmoveSettings.autoHop = ( g_pmove_autoHop_cvar.integer != 0 );
	g_pmoveSettings.bunnyHop = ( g_pmove_bunnyHop_cvar.integer != 0 );
	g_pmoveSettings.chainJump = g_pmove_chainJump_cvar.integer;
	g_pmoveSettings.chainJumpVelocity = g_pmove_chainJumpVelocity_cvar.value;
	g_pmoveSettings.circleStrafeFriction = g_pmove_circleStrafeFriction_cvar.value;
	g_pmoveSettings.crouchSlide = ( g_pmove_crouchSlide_cvar.integer != 0 );
	g_pmoveSettings.crouchSlideFriction = g_pmove_crouchSlideFriction_cvar.value;
	g_pmoveSettings.crouchSlideTime = g_pmove_crouchSlideTime_cvar.integer;
	g_pmoveSettings.crouchStepJump = ( g_pmove_crouchStepJump_cvar.integer != 0 );
	g_pmoveSettings.doubleJump = ( g_pmove_doubleJump_cvar.integer != 0 );
	g_pmoveSettings.jumpTimeDeltaMin = g_pmove_jumpTimeDeltaMin_cvar.value;
	g_pmoveSettings.jumpVelocity = g_pmove_jumpVelocity_cvar.value;
	g_pmoveSettings.jumpVelocityMax = g_pmove_jumpVelocityMax_cvar.value;
	g_pmoveSettings.jumpVelocityScaleAdd = g_pmove_jumpVelocityScaleAdd_cvar.value;
	g_pmoveSettings.jumpVelocityTimeThreshold = G_PmoveClampRetailMinPositive( g_pmove_jumpVelocityTimeThreshold_cvar.value );
	g_pmoveSettings.jumpVelocityTimeThresholdOffset = G_PmoveClampRetailMinPositive( g_pmove_jumpVelocityTimeThresholdOffset_cvar.value );
	{
		qboolean	noPlayerClip;

		noPlayerClip = ( g_pmove_noPlayerClip_cvar.integer != 0 );
		if ( g_instaGib.integer != 0 ) {
			noPlayerClip = qtrue;
		}

		g_pmoveSettings.noPlayerClip = noPlayerClip;
	}
	g_pmoveSettings.rampJump = ( g_pmove_rampJump_cvar.integer != 0 );
	g_pmoveSettings.rampJumpScale = g_pmove_rampJumpScale_cvar.value;
	g_pmoveSettings.stepHeight = g_pmove_stepHeight_cvar.value;
	g_pmoveSettings.stepJump = ( g_pmove_stepJump_cvar.integer != 0 );
	g_pmoveSettings.stepJumpVelocity = g_pmove_stepJumpVelocity_cvar.value;
	g_pmoveSettings.strafeAccel = g_pmove_strafeAccel_cvar.value;
	g_pmoveSettings.velocityGh = G_PmoveClampRetailMinPositive( g_pmove_velocityGh_cvar.value );
	g_pmoveSettings.walkAccel = g_pmove_walkAccel_cvar.value;
	g_pmoveSettings.walkFriction = g_pmove_walkFriction_cvar.value;
	g_pmoveSettings.waterSwimScale = g_pmove_waterSwimScale_cvar.value;
	g_pmoveSettings.waterWadeScale = g_pmove_waterWadeScale_cvar.value;
	g_pmoveSettings.weaponDropTime = g_pmove_weaponDropTime_cvar.integer;
	g_pmoveSettings.weaponRaiseTime = g_pmove_weaponRaiseTime_cvar.integer;
	g_pmoveSettings.wishSpeed = g_pmove_wishSpeed_cvar.value;
	{
		float	machinegunIronsightsScale;

		machinegunIronsightsScale = g_weaponConfig.machinegunIronsightsScale;
		if ( machinegunIronsightsScale <= 0.0f ) {
			machinegunIronsightsScale = defaults ? defaults->machinegunIronsightsScale : 1.0f;
		}

		g_pmoveSettings.machinegunIronsightsScale = machinegunIronsightsScale;
	}
	{
		float	gauntletSpeedFactor;

		gauntletSpeedFactor = g_weaponConfig.gauntletSpeedFactor;
		if ( gauntletSpeedFactor <= 0.0f ) {
			gauntletSpeedFactor = defaults ? defaults->gauntletSpeedFactor : 1.0f;
		}

		g_pmoveSettings.gauntletSpeedFactor = gauntletSpeedFactor;
	}
	g_pmoveSettings.midAirMinimumHeight = g_weaponConfig.midAirMinimumHeight;
	g_pmoveSettings.nailgunBounceEnabled = ( g_weaponConfig.nailgunBounceEnabled != 0 );
	g_pmoveSettings.nailgunBouncePercentage = g_weaponConfig.nailgunBouncePercentage;
	g_pmoveSettings.quadDamageMultiplier = ( g_weaponConfig.quadDamageMultiplier > 0.0f ) ? g_weaponConfig.quadDamageMultiplier : ( defaults ? defaults->quadDamageMultiplier : 1.0f );
	g_pmoveSettings.guidedRocketEnabled = ( g_weaponConfig.guidedRocketEnabled != 0 );
	g_pmoveSettings.quadHogEnabled = g_weaponConfig.quadHogEnabled;
	g_pmoveSettings.quadHogIdleSeconds = g_weaponConfig.quadHogIdleSeconds;
	g_pmoveSettings.quadHogTimeSeconds = g_weaponConfig.quadHogTimeSeconds;
	g_pmoveSettings.quadHogPingRateSeconds = g_weaponConfig.quadHogPingRateSeconds;

	{
		weapon_t	weapon;

		for ( weapon = WP_NONE; weapon < WP_NUM_WEAPONS; ++weapon ) {
			int	overrideReload;
			int	reload;

			overrideReload = g_pmoveWeaponReloadOverrides[weapon];
			reload = overrideReload;
			if ( reload <= 0 ) {
				reload = G_PmoveDefaultWeaponReloadTime( weapon );
			}

			g_pmoveSettings.weaponReloadOverrides[weapon] = overrideReload;
			g_pmoveSettings.weaponReloadTimes[weapon] = reload;
		}
	}
	G_PmovePublishSettings( qfalse );
}

/*
=============
G_PmoveStoreWeaponReloads

Caches reload durations from the gameplay configuration for pmove consumers.
=============
*/
void G_PmoveStoreWeaponReloads( const weaponReloadConfig_t *config ) {
	weapon_t	weapon;

	for ( weapon = WP_NONE; weapon < WP_NUM_WEAPONS; ++weapon ) {
		int	duration = 0;

		if ( config ) {
			switch ( weapon ) {
			case WP_GAUNTLET:
				duration = config->gauntlet;
				break;
			case WP_MACHINEGUN:
				duration = config->machinegun;
				break;
			case WP_SHOTGUN:
				duration = config->shotgun;
				break;
			case WP_GRENADE_LAUNCHER:
				duration = config->grenadeLauncher;
				break;
			case WP_ROCKET_LAUNCHER:
				duration = config->rocketLauncher;
				break;
			case WP_LIGHTNING:
				duration = config->lightningGun;
				break;
			case WP_RAILGUN:
				duration = config->railgun;
				break;
			case WP_PLASMAGUN:
				duration = config->plasmagun;
				break;
			case WP_BFG:
				duration = config->bfg;
				break;
			case WP_GRAPPLING_HOOK:
				duration = config->grapplingHook;
				break;
			case WP_HEAVY_MACHINEGUN:
				duration = config->heavyMachinegun;
				break;
			case WP_NAILGUN:
				duration = config->nailgun;
				break;
			case WP_PROX_LAUNCHER:
				duration = config->proximityLauncher;
				break;
			case WP_CHAINGUN:
				duration = config->chaingun;
				break;
			default:
				duration = 0;
				break;
			}
		}

		g_pmoveWeaponReloadOverrides[weapon] = duration;
	}

	g_pmove_force_update = qtrue;
}

/*
=============
G_PmoveResetFactoryManagedCvars

Restores every factory-owned cvar surface that feeds the published pmove
settings payload before a new factory layers overrides on top.
=============
*/
void G_PmoveResetFactoryManagedCvars( void ) {
	trap_Cvar_Set( "pmove_AirAccel", "1.0f" );
	trap_Cvar_Set( "pmove_AirControl", "0" );
	trap_Cvar_Set( "pmove_AirStepFriction", "0.03f" );
	trap_Cvar_Set( "pmove_AirSteps", "1" );
	trap_Cvar_Set( "pmove_AirStopAccel", "1.0f" );
	trap_Cvar_Set( "pmove_AutoHop", "1" );
	trap_Cvar_Set( "pmove_BunnyHop", "1" );
	trap_Cvar_Set( "pmove_ChainJump", "1" );
	trap_Cvar_Set( "pmove_ChainJumpVelocity", "110.0f" );
	trap_Cvar_Set( "pmove_CircleStrafeFriction", "6.0f" );
	trap_Cvar_Set( "pmove_CrouchSlide", "0" );
	trap_Cvar_Set( "pmove_CrouchSlideFriction", "0.5f" );
	trap_Cvar_Set( "pmove_CrouchSlideTime", "2000" );
	trap_Cvar_Set( "pmove_CrouchStepJump", "1" );
	trap_Cvar_Set( "pmove_DoubleJump", "0" );
	trap_Cvar_Set( "pmove_JumpTimeDeltaMin", "100.0f" );
	trap_Cvar_Set( "pmove_JumpVelocity", "275.0f" );
	trap_Cvar_Set( "pmove_JumpVelocityMax", "700.0f" );
	trap_Cvar_Set( "pmove_JumpVelocityScaleAdd", "0.4f" );
	trap_Cvar_Set( "pmove_JumpVelocityTimeThreshold", "500.0f" );
	trap_Cvar_Set( "pmove_JumpVelocityTimeThresholdOffset", "0.6f" );
	trap_Cvar_Set( "pmove_noPlayerClip", "0" );
	trap_Cvar_Set( "g_instaGib", "0" );
	trap_Cvar_Set( "pmove_RampJump", "0" );
	trap_Cvar_Set( "pmove_RampJumpScale", "1.0f" );
	trap_Cvar_Set( "pmove_StepHeight", "22.0f" );
	trap_Cvar_Set( "pmove_StepJump", "1" );
	trap_Cvar_Set( "pmove_StepJumpVelocity", "48.0f" );
	trap_Cvar_Set( "pmove_StrafeAccel", "1.0f" );
	trap_Cvar_Set( "pmove_velocity_gh", "800" );
	trap_Cvar_Set( "g_velocity_gh", "1800" );
	trap_Cvar_Set( "pmove_WalkAccel", "10.0f" );
	trap_Cvar_Set( "pmove_WalkFriction", "6.0f" );
	trap_Cvar_Set( "pmove_WaterSwimScale", "0.6f" );
	trap_Cvar_Set( "pmove_WaterWadeScale", "0.8f" );
	trap_Cvar_Set( "pmove_WeaponDropTime", "200" );
	trap_Cvar_Set( "pmove_WeaponRaiseTime", "200" );
	trap_Cvar_Set( "pmove_WishSpeed", "400.0f" );
	trap_Cvar_Set( "g_gauntletSpeedFactor", "1.0" );
	trap_Cvar_Set( "g_ironsights_mg", "1.0" );
	trap_Cvar_Set( "g_midAirMinHeight", "96" );
	trap_Cvar_Set( "g_nailbounce", "1" );
	trap_Cvar_Set( "g_nailbouncepercentage", "65" );
	trap_Cvar_Set( "g_quadDamageFactor", "3" );
	trap_Cvar_Set( "g_guidedRocket", "0" );
	trap_Cvar_Set( "g_quadHog", "0" );
	trap_Cvar_Set( "g_quadHogIdle", "0" );
	trap_Cvar_Set( "g_quadHogTime", "0" );
	trap_Cvar_Set( "g_quadHogPingRate", "0" );

	g_pmove_force_update = qtrue;
}

/*
=============
G_RegisterPmoveCvars

Registers all Quake Live pmove tuning cvars.
=============
*/
void G_RegisterPmoveCvars( void ) {
	G_PmoveRegisterCvar( &g_pmove_airAccel_cvar, "pmove_AirAccel", "1.0f", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );
	G_PmoveRegisterCvar( &g_pmove_airControl_cvar, "pmove_AirControl", "0", PMOVE_CVAR_FLAGS_CUSTOM );
	G_PmoveRegisterCvar( &g_pmove_airStepFriction_cvar, "pmove_AirStepFriction", "0.03f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_airSteps_cvar, "pmove_AirSteps", "1", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );
	G_PmoveRegisterCvar( &g_pmove_airStopAccel_cvar, "pmove_AirStopAccel", "1.0f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_autoHop_cvar, "pmove_AutoHop", "1", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_bunnyHop_cvar, "pmove_BunnyHop", "1", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_chainJump_cvar, "pmove_ChainJump", "1", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_chainJumpVelocity_cvar, "pmove_ChainJumpVelocity", "110.0f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_circleStrafeFriction_cvar, "pmove_CircleStrafeFriction", "6.0f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_crouchSlide_cvar, "pmove_CrouchSlide", "0", PMOVE_CVAR_FLAGS_FACTORY_ONLY );
	G_PmoveRegisterCvar( &g_pmove_crouchSlideFriction_cvar, "pmove_CrouchSlideFriction", "0.5f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_crouchSlideTime_cvar, "pmove_CrouchSlideTime", "2000", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_crouchStepJump_cvar, "pmove_CrouchStepJump", "1", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_doubleJump_cvar, "pmove_DoubleJump", "0", PMOVE_CVAR_FLAGS_FACTORY_ONLY );
	G_PmoveRegisterCvar( &g_pmove_jumpTimeDeltaMin_cvar, "pmove_JumpTimeDeltaMin", "100.0f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_jumpVelocity_cvar, "pmove_JumpVelocity", "275.0f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_jumpVelocityMax_cvar, "pmove_JumpVelocityMax", "700.0f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_jumpVelocityScaleAdd_cvar, "pmove_JumpVelocityScaleAdd", "0.4f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_jumpVelocityTimeThreshold_cvar, "pmove_JumpVelocityTimeThreshold", "500.0f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_jumpVelocityTimeThresholdOffset_cvar, "pmove_JumpVelocityTimeThresholdOffset", "0.6f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_noPlayerClip_cvar, "pmove_noPlayerClip", "0", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );
	G_PmoveRegisterCvar( &g_pmove_rampJump_cvar, "pmove_RampJump", "0", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );
	G_PmoveRegisterCvar( &g_pmove_rampJumpScale_cvar, "pmove_RampJumpScale", "1.0f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_stepHeight_cvar, "pmove_StepHeight", "22.0f", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );
	G_PmoveRegisterCvar( &g_pmove_stepJump_cvar, "pmove_StepJump", "1", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );
	G_PmoveRegisterCvar( &g_pmove_stepJumpVelocity_cvar, "pmove_StepJumpVelocity", "48.0f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_strafeAccel_cvar, "pmove_StrafeAccel", "1.0f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_velocityGh_cvar, "pmove_velocity_gh", "800", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );
	G_PmoveRegisterCvar( &g_pmove_walkAccel_cvar, "pmove_WalkAccel", "10.0f", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );
	G_PmoveRegisterCvar( &g_pmove_walkFriction_cvar, "pmove_WalkFriction", "6.0f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_waterSwimScale_cvar, "pmove_WaterSwimScale", "0.6f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_waterWadeScale_cvar, "pmove_WaterWadeScale", "0.8f", PMOVE_CVAR_FLAGS_FACTORY );
	G_PmoveRegisterCvar( &g_pmove_weaponDropTime_cvar, "pmove_WeaponDropTime", "200", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );
	G_PmoveRegisterCvar( &g_pmove_weaponRaiseTime_cvar, "pmove_WeaponRaiseTime", "200", PMOVE_CVAR_FLAGS_CUSTOM_LATCH );
	G_PmoveRegisterCvar( &g_pmove_wishSpeed_cvar, "pmove_WishSpeed", "400.0f", PMOVE_CVAR_FLAGS_FACTORY );

	g_pmove_force_update = qtrue;
	G_RefreshPmoveSettings();
}

/*
=============
G_RefreshPmoveSettings

Updates the cached pmove settings if a new server frame has begun.
=============
*/
void G_RefreshPmoveSettings( void ) {
	if ( !g_pmove_force_update && level.framenum == g_pmove_last_frame ) {
		return;
	}

	G_PmoveUpdateCvar( &g_pmove_airAccel_cvar, "pmove_AirAccel", qtrue );
	G_PmoveUpdateCvar( &g_pmove_airControl_cvar, "pmove_AirControl", qfalse );
	G_PmoveUpdateCvar( &g_pmove_airStepFriction_cvar, "pmove_AirStepFriction", qtrue );
	G_PmoveUpdateCvar( &g_pmove_airSteps_cvar, "pmove_AirSteps", qtrue );
	G_PmoveUpdateCvar( &g_pmove_airStopAccel_cvar, "pmove_AirStopAccel", qtrue );
	G_PmoveUpdateCvar( &g_pmove_autoHop_cvar, "pmove_AutoHop", qtrue );
	G_PmoveUpdateCvar( &g_pmove_bunnyHop_cvar, "pmove_BunnyHop", qtrue );
	G_PmoveUpdateCvar( &g_pmove_chainJump_cvar, "pmove_ChainJump", qtrue );
	G_PmoveUpdateCvar( &g_pmove_chainJumpVelocity_cvar, "pmove_ChainJumpVelocity", qtrue );
	G_PmoveUpdateCvar( &g_pmove_circleStrafeFriction_cvar, "pmove_CircleStrafeFriction", qtrue );
	G_PmoveUpdateCvar( &g_pmove_crouchSlide_cvar, "pmove_CrouchSlide", qfalse );
	G_PmoveUpdateCvar( &g_pmove_crouchSlideFriction_cvar, "pmove_CrouchSlideFriction", qtrue );
	G_PmoveUpdateCvar( &g_pmove_crouchSlideTime_cvar, "pmove_CrouchSlideTime", qtrue );
	G_PmoveUpdateCvar( &g_pmove_crouchStepJump_cvar, "pmove_CrouchStepJump", qtrue );
	G_PmoveUpdateCvar( &g_pmove_doubleJump_cvar, "pmove_DoubleJump", qfalse );
	G_PmoveUpdateCvar( &g_pmove_jumpTimeDeltaMin_cvar, "pmove_JumpTimeDeltaMin", qtrue );
	G_PmoveUpdateCvar( &g_pmove_jumpVelocity_cvar, "pmove_JumpVelocity", qtrue );
	G_PmoveUpdateCvar( &g_pmove_jumpVelocityMax_cvar, "pmove_JumpVelocityMax", qtrue );
	G_PmoveUpdateCvar( &g_pmove_jumpVelocityScaleAdd_cvar, "pmove_JumpVelocityScaleAdd", qtrue );
	G_PmoveUpdateCvar( &g_pmove_jumpVelocityTimeThreshold_cvar, "pmove_JumpVelocityTimeThreshold", qtrue );
	G_PmoveUpdateCvar( &g_pmove_jumpVelocityTimeThresholdOffset_cvar, "pmove_JumpVelocityTimeThresholdOffset", qtrue );
	G_PmoveUpdateCvar( &g_pmove_noPlayerClip_cvar, "pmove_noPlayerClip", qtrue );
	G_PmoveUpdateCvar( &g_instaGib, "g_instaGib", qfalse );
	G_PmoveUpdateCvar( &g_pmove_rampJump_cvar, "pmove_RampJump", qtrue );
	G_PmoveUpdateCvar( &g_pmove_rampJumpScale_cvar, "pmove_RampJumpScale", qtrue );
	G_PmoveUpdateCvar( &g_pmove_stepHeight_cvar, "pmove_StepHeight", qtrue );
	G_PmoveUpdateCvar( &g_pmove_stepJump_cvar, "pmove_StepJump", qtrue );
	G_PmoveUpdateCvar( &g_pmove_stepJumpVelocity_cvar, "pmove_StepJumpVelocity", qtrue );
	G_PmoveUpdateCvar( &g_pmove_strafeAccel_cvar, "pmove_StrafeAccel", qtrue );
	G_PmoveUpdateCvar( &g_pmove_velocityGh_cvar, "pmove_velocity_gh", qtrue );
	G_PmoveUpdateCvar( &g_pmove_walkAccel_cvar, "pmove_WalkAccel", qtrue );
	G_PmoveUpdateCvar( &g_pmove_walkFriction_cvar, "pmove_WalkFriction", qtrue );
	G_PmoveUpdateCvar( &g_pmove_waterSwimScale_cvar, "pmove_WaterSwimScale", qtrue );
	G_PmoveUpdateCvar( &g_pmove_waterWadeScale_cvar, "pmove_WaterWadeScale", qtrue );
	G_PmoveUpdateCvar( &g_pmove_weaponDropTime_cvar, "pmove_WeaponDropTime", qtrue );
	G_PmoveUpdateCvar( &g_pmove_weaponRaiseTime_cvar, "pmove_WeaponRaiseTime", qtrue );
	G_PmoveUpdateCvar( &g_pmove_wishSpeed_cvar, "pmove_WishSpeed", qtrue );

	G_PmoveCacheSettings();

	g_pmove_last_frame = level.framenum;
	g_pmove_force_update = qfalse;
}

/*
=============
G_PmoveHasAirControlCustomSetting

Returns whether the retail air-control custom-setting bit should be raised.
=============
*/
qboolean G_PmoveHasAirControlCustomSetting( void ) {
	return ( g_pmove_airControl_cvar.value != 0.0f ) ? qtrue : qfalse;
}

/*
=============
G_PmoveHasRampJumpCustomSetting

Returns whether the retail ramp-jump custom-setting bit should be raised.
=============
*/
qboolean G_PmoveHasRampJumpCustomSetting( void ) {
	return ( g_pmove_rampJump_cvar.integer != 0 ) ? qtrue : qfalse;
}

/*
=============
G_PmoveHasPhysicsCustomSetting

Returns whether the retail physics custom-setting bit should be raised for the
movement cvar slab owned by qagame.
=============
*/
qboolean G_PmoveHasPhysicsCustomSetting( void ) {
	if ( g_pmove_airAccel_cvar.value != 1.0f ) {
		return qtrue;
	}
	if ( g_pmove_walkAccel_cvar.value != 10.0f ) {
		return qtrue;
	}
	if ( g_pmove_walkFriction_cvar.value != 6.0f ) {
		return qtrue;
	}
	if ( g_pmove_airSteps_cvar.integer != 1 ) {
		return qtrue;
	}
	if ( g_pmove_bunnyHop_cvar.integer != 1 ) {
		return qtrue;
	}
	if ( g_pmove_stepJump_cvar.integer != 1 ) {
		return qtrue;
	}
	if ( g_pmove_stepHeight_cvar.value != 22.0f ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
G_PmoveHasWeaponSwitchingCustomSetting

Returns whether retail weapon raise/drop timings differ from their stock values.
=============
*/
qboolean G_PmoveHasWeaponSwitchingCustomSetting( void ) {
	if ( g_pmove_weaponRaiseTime_cvar.integer != 200 ) {
		return qtrue;
	}
	if ( g_pmove_weaponDropTime_cvar.integer != 200 ) {
		return qtrue;
	}

	return qfalse;
}

/*
=============
G_PmoveHasNoPlayerClipCustomSetting

Returns whether the retail no-player-clip custom-setting bit should be raised.
=============
*/
qboolean G_PmoveHasNoPlayerClipCustomSetting( void ) {
	return ( g_pmove_noPlayerClip_cvar.integer != 0 ) ? qtrue : qfalse;
}

/*
=============
G_PmoveHasGrappleVelocityCustomSetting

Returns whether the hook velocity override surface differs from retail defaults.
=============
*/
qboolean G_PmoveHasGrappleVelocityCustomSetting( void ) {
	return ( g_pmove_velocityGh_cvar.value != 800.0f ) ? qtrue : qfalse;
}
