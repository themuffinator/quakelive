#include <stdarg.h>
#include "g_local.h"

#define PMOVE_CVAR_FLAGS 0

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

Encodes the active pmove settings into a JSON payload for configstring broadcasts.
=============
*/
static qboolean G_PmoveSerializeSettings( const pmove_settings_t *settings, char *buffer, size_t bufferSize ) {
	size_t length = 0;
	weapon_t weapon;

	if ( !settings || !buffer || bufferSize == 0 ) {
		return qfalse;
	}

	buffer[0] = '\0';

	if ( !G_PmoveAppendPayload( buffer, bufferSize, &length, "{" ) ) {
		return qfalse;
	}

#define PMOVE_BOOL_FIELD( name ) \
	if ( !G_PmoveAppendPayload( buffer, bufferSize, &length, "\"%s\":%s,", #name, settings->name ? "true" : "false" ) ) { \
		return qfalse; \
	}

#define PMOVE_INT_FIELD( name ) \
	if ( !G_PmoveAppendPayload( buffer, bufferSize, &length, "\"%s\":%i,", #name, settings->name ) ) { \
		return qfalse; \
	}

#define PMOVE_FLOAT_FIELD( name ) \
	if ( !G_PmoveAppendPayload( buffer, bufferSize, &length, "\"%s\":%.6f,", #name, settings->name ) ) { \
		return qfalse; \
	}

	PMOVE_FLOAT_FIELD( airAccel );
	PMOVE_FLOAT_FIELD( airControl );
	PMOVE_FLOAT_FIELD( airStepFriction );
	PMOVE_INT_FIELD( airSteps );
	PMOVE_FLOAT_FIELD( airStopAccel );
	PMOVE_BOOL_FIELD( autoHop );
	PMOVE_BOOL_FIELD( bunnyHop );
	PMOVE_BOOL_FIELD( chainJump );
	PMOVE_FLOAT_FIELD( chainJumpVelocity );
	PMOVE_FLOAT_FIELD( circleStrafeFriction );
	PMOVE_BOOL_FIELD( crouchSlide );
	PMOVE_FLOAT_FIELD( crouchSlideFriction );
	PMOVE_INT_FIELD( crouchSlideTime );
	PMOVE_FLOAT_FIELD( flightThrust );
	PMOVE_BOOL_FIELD( crouchStepJump );
	PMOVE_BOOL_FIELD( doubleJump );
	PMOVE_FLOAT_FIELD( jumpTimeDeltaMin );
	PMOVE_FLOAT_FIELD( jumpVelocity );
	PMOVE_FLOAT_FIELD( jumpVelocityMax );
	PMOVE_FLOAT_FIELD( jumpVelocityScaleAdd );
	PMOVE_FLOAT_FIELD( jumpVelocityTimeThreshold );
	PMOVE_FLOAT_FIELD( jumpVelocityTimeThresholdOffset );
	PMOVE_BOOL_FIELD( noPlayerClip );
	PMOVE_BOOL_FIELD( rampJump );
	PMOVE_FLOAT_FIELD( rampJumpScale );
	PMOVE_FLOAT_FIELD( stepHeight );
	PMOVE_BOOL_FIELD( stepJump );
	PMOVE_FLOAT_FIELD( stepJumpVelocity );
	PMOVE_FLOAT_FIELD( strafeAccel );
	PMOVE_FLOAT_FIELD( velocityGh );
	PMOVE_FLOAT_FIELD( walkAccel );
	PMOVE_FLOAT_FIELD( walkFriction );
	PMOVE_FLOAT_FIELD( waterSwimScale );
	PMOVE_FLOAT_FIELD( waterWadeScale );
	PMOVE_INT_FIELD( weaponDropTime );
	PMOVE_INT_FIELD( weaponRaiseTime );
	PMOVE_FLOAT_FIELD( wishSpeed );

#undef PMOVE_BOOL_FIELD
#undef PMOVE_INT_FIELD
#undef PMOVE_FLOAT_FIELD

	if ( !G_PmoveAppendPayload( buffer, bufferSize, &length, "\"weaponReloadTimes\":[" ) ) {
		return qfalse;
	}

	for ( weapon = WP_NONE; weapon < WP_NUM_WEAPONS; ++weapon ) {
		const char *separator = ( weapon == WP_NONE ) ? "" : ",";
		if ( !G_PmoveAppendPayload( buffer, bufferSize, &length, "%s%i", separator, settings->weaponReloadTimes[weapon] ) ) {
			return qfalse;
		}
	}

	if ( !G_PmoveAppendPayload( buffer, bufferSize, &length, "]}" ) ) {
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
G_PmoveRegisterCvar

Registers a pmove tuning cvar with the VM bridge.
=============
*/
static void G_PmoveRegisterCvar( vmCvar_t *vmCvar, const char *name, const char *defaultValue ) {
	trap_Cvar_Register( vmCvar, name, defaultValue, PMOVE_CVAR_FLAGS );
}

/*
=============
G_PmoveUpdateCvar

Synchronizes a pmove tuning cvar mirror.
=============
*/
static void G_PmoveUpdateCvar( vmCvar_t *vmCvar ) {
	if ( vmCvar ) {
		trap_Cvar_Update( vmCvar );
	}
}

/*
=============
G_PmoveDefaultWeaponReloadTime

Provides the compiled reload fallback for a specific weapon slot.
=============
*/
static int G_PmoveDefaultWeaponReloadTime( weapon_t weapon ) {
	switch ( weapon ) {
	case WP_GAUNTLET:
		return 400;
	case WP_MACHINEGUN:
		return 100;
	case WP_SHOTGUN:
		return 1000;
	case WP_GRENADE_LAUNCHER:
		return 800;
	case WP_ROCKET_LAUNCHER:
		return 800;
	case WP_LIGHTNING:
		return 50;
	case WP_RAILGUN:
		return 1500;
	case WP_PLASMAGUN:
		return 100;
	case WP_BFG:
		return 200;
	case WP_GRAPPLING_HOOK:
		return 400;
	case WP_HEAVY_MACHINEGUN:
		return 75;
	case WP_NAILGUN:
		return 1000;
	case WP_PROX_LAUNCHER:
		return 800;
	case WP_CHAINGUN:
		return 30;
	default:
		return 0;
	}
}

/*
=============
G_PmoveCacheSettings

Copies the latched pmove cvar values into the live movement settings.
=============
*/
static void G_PmoveCacheSettings( void ) {
	g_pmoveSettings.airAccel = g_pmove_airAccel_cvar.value;
	g_pmoveSettings.airControl = g_pmove_airControl_cvar.value;
	g_pmoveSettings.airStepFriction = g_pmove_airStepFriction_cvar.value;
	g_pmoveSettings.airSteps = g_pmove_airSteps_cvar.integer;
	g_pmoveSettings.airStopAccel = g_pmove_airStopAccel_cvar.value;
	g_pmoveSettings.autoHop = ( g_pmove_autoHop_cvar.integer != 0 );
	g_pmoveSettings.bunnyHop = ( g_pmove_bunnyHop_cvar.integer != 0 );
	g_pmoveSettings.chainJump = ( g_pmove_chainJump_cvar.integer != 0 );
	g_pmoveSettings.chainJumpVelocity = g_pmove_chainJumpVelocity_cvar.value;
	g_pmoveSettings.circleStrafeFriction = g_pmove_circleStrafeFriction_cvar.value;
	g_pmoveSettings.crouchSlide = ( g_pmove_crouchSlide_cvar.integer != 0 );
	g_pmoveSettings.crouchSlideFriction = g_pmove_crouchSlideFriction_cvar.value;
	g_pmoveSettings.crouchSlideTime = g_pmove_crouchSlideTime_cvar.integer;
	g_pmoveSettings.flightThrust = ( g_flightThrust.value > 0.0f ) ? g_flightThrust.value : 0.0f;
	g_pmoveSettings.crouchStepJump = ( g_pmove_crouchStepJump_cvar.integer != 0 );
	g_pmoveSettings.doubleJump = ( g_pmove_doubleJump_cvar.integer != 0 );
	g_pmoveSettings.jumpTimeDeltaMin = g_pmove_jumpTimeDeltaMin_cvar.value;
	g_pmoveSettings.jumpVelocity = g_pmove_jumpVelocity_cvar.value;
	g_pmoveSettings.jumpVelocityMax = g_pmove_jumpVelocityMax_cvar.value;
	g_pmoveSettings.jumpVelocityScaleAdd = g_pmove_jumpVelocityScaleAdd_cvar.value;
	g_pmoveSettings.jumpVelocityTimeThreshold = g_pmove_jumpVelocityTimeThreshold_cvar.value;
	g_pmoveSettings.jumpVelocityTimeThresholdOffset = g_pmove_jumpVelocityTimeThresholdOffset_cvar.value;
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
	{
		float	grappleSpeed;

		grappleSpeed = ( float )g_weaponConfig.grappleSpeed;
		if ( grappleSpeed <= 0.0f ) {
			grappleSpeed = g_pmove_velocityGh_cvar.value;
			if ( grappleSpeed <= 0.0f ) {
				grappleSpeed = pm_defaultSettings.velocityGh;
			}
		}

		g_pmoveSettings.velocityGh = grappleSpeed;
	}
	g_pmoveSettings.walkAccel = g_pmove_walkAccel_cvar.value;
	g_pmoveSettings.walkFriction = g_pmove_walkFriction_cvar.value;
	g_pmoveSettings.waterSwimScale = g_pmove_waterSwimScale_cvar.value;
	g_pmoveSettings.waterWadeScale = g_pmove_waterWadeScale_cvar.value;
	g_pmoveSettings.weaponDropTime = g_pmove_weaponDropTime_cvar.integer;
	g_pmoveSettings.weaponRaiseTime = g_pmove_weaponRaiseTime_cvar.integer;
	g_pmoveSettings.wishSpeed = g_pmove_wishSpeed_cvar.value;

	{
		weapon_t	weapon;

		for ( weapon = WP_NONE; weapon < WP_NUM_WEAPONS; ++weapon ) {
			int	reload;

			reload = g_pmoveWeaponReloadOverrides[weapon];
			if ( reload <= 0 ) {
				reload = G_PmoveDefaultWeaponReloadTime( weapon );
			}

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

		if ( duration <= 0 ) {
			duration = G_PmoveDefaultWeaponReloadTime( weapon );
		}

		g_pmoveWeaponReloadOverrides[weapon] = duration;
	}

	g_pmove_force_update = qtrue;
}

/*
=============
G_RegisterPmoveCvars

Registers all Quake Live pmove tuning cvars.
=============
*/
void G_RegisterPmoveCvars( void ) {
	G_PmoveRegisterCvar( &g_pmove_airAccel_cvar, "pmove_AirAccel", "1.0f" );
	G_PmoveRegisterCvar( &g_pmove_airControl_cvar, "pmove_AirControl", "0" );
	G_PmoveRegisterCvar( &g_pmove_airStepFriction_cvar, "pmove_AirStepFriction", "0.03f" );
	G_PmoveRegisterCvar( &g_pmove_airSteps_cvar, "pmove_AirSteps", "1" );
	G_PmoveRegisterCvar( &g_pmove_airStopAccel_cvar, "pmove_AirStopAccel", "1.0f" );
	G_PmoveRegisterCvar( &g_pmove_autoHop_cvar, "pmove_AutoHop", "1" );
	G_PmoveRegisterCvar( &g_pmove_bunnyHop_cvar, "pmove_BunnyHop", "1" );
	G_PmoveRegisterCvar( &g_pmove_chainJump_cvar, "pmove_ChainJump", "1" );
	G_PmoveRegisterCvar( &g_pmove_chainJumpVelocity_cvar, "pmove_ChainJumpVelocity", "110.0f" );
	G_PmoveRegisterCvar( &g_pmove_circleStrafeFriction_cvar, "pmove_CircleStrafeFriction", "6.0f" );
	G_PmoveRegisterCvar( &g_pmove_crouchSlide_cvar, "pmove_CrouchSlide", "0" );
	G_PmoveRegisterCvar( &g_pmove_crouchSlideFriction_cvar, "pmove_CrouchSlideFriction", "0.5f" );
	G_PmoveRegisterCvar( &g_pmove_crouchSlideTime_cvar, "pmove_CrouchSlideTime", "2000" );
	G_PmoveRegisterCvar( &g_pmove_crouchStepJump_cvar, "pmove_CrouchStepJump", "1" );
	G_PmoveRegisterCvar( &g_pmove_doubleJump_cvar, "pmove_DoubleJump", "0" );
	G_PmoveRegisterCvar( &g_pmove_jumpTimeDeltaMin_cvar, "pmove_JumpTimeDeltaMin", "100.0f" );
	G_PmoveRegisterCvar( &g_pmove_jumpVelocity_cvar, "pmove_JumpVelocity", "275.0f" );
	G_PmoveRegisterCvar( &g_pmove_jumpVelocityMax_cvar, "pmove_JumpVelocityMax", "700.0f" );
	G_PmoveRegisterCvar( &g_pmove_jumpVelocityScaleAdd_cvar, "pmove_JumpVelocityScaleAdd", "0.4f" );
	G_PmoveRegisterCvar( &g_pmove_jumpVelocityTimeThreshold_cvar, "pmove_JumpVelocityTimeThreshold", "500.0f" );
	G_PmoveRegisterCvar( &g_pmove_jumpVelocityTimeThresholdOffset_cvar, "pmove_JumpVelocityTimeThresholdOffset", "0.6f" );
	G_PmoveRegisterCvar( &g_pmove_noPlayerClip_cvar, "pmove_noPlayerClip", "0" );
	G_PmoveRegisterCvar( &g_pmove_rampJump_cvar, "pmove_RampJump", "0" );
	G_PmoveRegisterCvar( &g_pmove_rampJumpScale_cvar, "pmove_RampJumpScale", "1.0f" );
	G_PmoveRegisterCvar( &g_pmove_stepHeight_cvar, "pmove_StepHeight", "22.0f" );
	G_PmoveRegisterCvar( &g_pmove_stepJump_cvar, "pmove_StepJump", "1" );
	G_PmoveRegisterCvar( &g_pmove_stepJumpVelocity_cvar, "pmove_StepJumpVelocity", "48.0f" );
	G_PmoveRegisterCvar( &g_pmove_strafeAccel_cvar, "pmove_StrafeAccel", "1.0f" );
	G_PmoveRegisterCvar( &g_pmove_velocityGh_cvar, "pmove_velocity_gh", "800" );
	G_PmoveRegisterCvar( &g_pmove_walkAccel_cvar, "pmove_WalkAccel", "10.0f" );
	G_PmoveRegisterCvar( &g_pmove_walkFriction_cvar, "pmove_WalkFriction", "6.0f" );
	G_PmoveRegisterCvar( &g_pmove_waterSwimScale_cvar, "pmove_WaterSwimScale", "0.6f" );
	G_PmoveRegisterCvar( &g_pmove_waterWadeScale_cvar, "pmove_WaterWadeScale", "0.8f" );
	G_PmoveRegisterCvar( &g_pmove_weaponDropTime_cvar, "pmove_WeaponDropTime", "200" );
	G_PmoveRegisterCvar( &g_pmove_weaponRaiseTime_cvar, "pmove_WeaponRaiseTime", "200" );
	G_PmoveRegisterCvar( &g_pmove_wishSpeed_cvar, "pmove_WishSpeed", "400.0f" );

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

	G_PmoveUpdateCvar( &g_pmove_airAccel_cvar );
	G_PmoveUpdateCvar( &g_pmove_airControl_cvar );
	G_PmoveUpdateCvar( &g_pmove_airStepFriction_cvar );
	G_PmoveUpdateCvar( &g_pmove_airSteps_cvar );
	G_PmoveUpdateCvar( &g_pmove_airStopAccel_cvar );
	G_PmoveUpdateCvar( &g_pmove_autoHop_cvar );
	G_PmoveUpdateCvar( &g_pmove_bunnyHop_cvar );
	G_PmoveUpdateCvar( &g_pmove_chainJump_cvar );
	G_PmoveUpdateCvar( &g_pmove_chainJumpVelocity_cvar );
	G_PmoveUpdateCvar( &g_pmove_circleStrafeFriction_cvar );
	G_PmoveUpdateCvar( &g_pmove_crouchSlide_cvar );
	G_PmoveUpdateCvar( &g_pmove_crouchSlideFriction_cvar );
	G_PmoveUpdateCvar( &g_pmove_crouchSlideTime_cvar );
	G_PmoveUpdateCvar( &g_pmove_crouchStepJump_cvar );
	G_PmoveUpdateCvar( &g_pmove_doubleJump_cvar );
	G_PmoveUpdateCvar( &g_pmove_jumpTimeDeltaMin_cvar );
	G_PmoveUpdateCvar( &g_pmove_jumpVelocity_cvar );
	G_PmoveUpdateCvar( &g_pmove_jumpVelocityMax_cvar );
	G_PmoveUpdateCvar( &g_pmove_jumpVelocityScaleAdd_cvar );
	G_PmoveUpdateCvar( &g_pmove_jumpVelocityTimeThreshold_cvar );
	G_PmoveUpdateCvar( &g_pmove_jumpVelocityTimeThresholdOffset_cvar );
	G_PmoveUpdateCvar( &g_pmove_noPlayerClip_cvar );
	G_PmoveUpdateCvar( &g_instaGib );
	G_PmoveUpdateCvar( &g_pmove_rampJump_cvar );
	G_PmoveUpdateCvar( &g_pmove_rampJumpScale_cvar );
	G_PmoveUpdateCvar( &g_pmove_stepHeight_cvar );
	G_PmoveUpdateCvar( &g_pmove_stepJump_cvar );
	G_PmoveUpdateCvar( &g_pmove_stepJumpVelocity_cvar );
	G_PmoveUpdateCvar( &g_pmove_strafeAccel_cvar );
	G_PmoveUpdateCvar( &g_pmove_velocityGh_cvar );
	G_PmoveUpdateCvar( &g_pmove_walkAccel_cvar );
	G_PmoveUpdateCvar( &g_pmove_walkFriction_cvar );
	G_PmoveUpdateCvar( &g_pmove_waterSwimScale_cvar );
	G_PmoveUpdateCvar( &g_pmove_waterWadeScale_cvar );
	G_PmoveUpdateCvar( &g_pmove_weaponDropTime_cvar );
	G_PmoveUpdateCvar( &g_pmove_weaponRaiseTime_cvar );
	G_PmoveUpdateCvar( &g_pmove_wishSpeed_cvar );
	trap_Cvar_Update( &g_flightThrust );

	G_PmoveCacheSettings();

	g_pmove_last_frame = level.framenum;
	g_pmove_force_update = qfalse;
}
