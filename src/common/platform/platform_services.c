#include "platform_services.h"

#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "platform_config.h"
#if QL_PLATFORM_HAS_STEAMWORKS
#include "platform_steamworks.h"
#endif

#ifndef QL_STEAMWORKS_RETRY_SECONDS
#define QL_STEAMWORKS_RETRY_SECONDS 5
#endif

static ql_platform_service_table ql_platformServices;
static qboolean ql_platformServicesInitialised;
#if QL_PLATFORM_HAS_STEAMWORKS
static qboolean ql_platformSteamworksInitialised;
static time_t ql_platformSteamworksNextAttemptTime;
#endif

/*
=============
QL_StringRepresentsTrue

Returns qtrue when an environment string should be treated as enabled.
=============
*/
static qboolean QL_StringRepresentsTrue( const char *value ) {
	if ( !value || !value[0] ) {
		return qfalse;
	}

	if ( value[0] == '0' && value[1] == '\0' ) {
		return qfalse;
	}

	if ( !Q_stricmp( value, "false" ) || !Q_stricmp( value, "no" ) || !Q_stricmp( value, "off" ) ) {
		return qfalse;
	}

	return qtrue;
}

/*
=============
QL_PlatformExternalEcosystemsDisableReason

Returns the runtime policy flag currently disabling platform integrations.
=============
*/
static const char *QL_PlatformExternalEcosystemsDisableReason( void ) {
	const char *flag;

	flag = getenv( "QL_DISABLE_EXTERNAL_ECOSYSTEMS" );
	if ( QL_StringRepresentsTrue( flag ) ) {
		return "QL_DISABLE_EXTERNAL_ECOSYSTEMS";
	}

	flag = getenv( "QL_DISABLE_STEAMWORKS" );
	if ( QL_StringRepresentsTrue( flag ) ) {
		return "QL_DISABLE_STEAMWORKS";
	}

	return NULL;
}

/*
=============
QL_PlatformExternalEcosystemsDisabled

Checks whether runtime platform integrations should be disabled.
=============
*/
static qboolean QL_PlatformExternalEcosystemsDisabled( void ) {
	return QL_PlatformExternalEcosystemsDisableReason() != NULL ? qtrue : qfalse;
}

#if QL_PLATFORM_HAS_STEAMWORKS || QL_PLATFORM_HAS_OPEN_STEAM || QL_PLATFORM_BUILD_HYBRID
/*
=============
QL_PlatformExternalEcosystemsDisableProviderLabel

Returns the descriptor provider label for the active runtime disable policy.
=============
*/
static const char *QL_PlatformExternalEcosystemsDisableProviderLabel( void ) {
	const char *reason;

	reason = QL_PlatformExternalEcosystemsDisableReason();
	if ( reason && !strcmp( reason, "QL_DISABLE_STEAMWORKS" ) ) {
		return "Disabled by QL_DISABLE_STEAMWORKS";
	}

	return "Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS";
}
#endif

/*
=============
QL_FinaliseDescriptor

Normalises a feature descriptor and assigns a fallback label when needed.
=============
*/
static void QL_FinaliseDescriptor( ql_platform_feature_descriptor *descriptor, const char *fallbackLabel ) {
	if ( !descriptor ) {
		return;
	}

	if ( !descriptor->compiled ) {
		descriptor->initialised = qfalse;
	}

	if ( !descriptor->provider && fallbackLabel ) {
		descriptor->provider = fallbackLabel;
	}
}

/*
=============
QL_DescribePlatformFeaturePolicy

Publishes a short policy label describing how one online-service descriptor
should be interpreted by the rest of the client/server surfaces.
=============
*/
const char *QL_DescribePlatformFeaturePolicy( const ql_platform_feature_descriptor *descriptor ) {
	const char *provider;

	if ( !descriptor ) {
		return "compatibility-unavailable";
	}

	provider = descriptor->provider ? descriptor->provider : "";

	if ( strstr( provider, "QL_BUILD_ONLINE_SERVICES=0" ) != NULL ) {
		return "compatibility-disabled (QL_BUILD_ONLINE_SERVICES=0)";
	}

	if ( strstr( provider, "QL_DISABLE_EXTERNAL_ECOSYSTEMS" ) != NULL ) {
		return "compatibility-disabled (QL_DISABLE_EXTERNAL_ECOSYSTEMS)";
	}

	if ( strstr( provider, "QL_DISABLE_STEAMWORKS" ) != NULL ) {
		return "compatibility-disabled (QL_DISABLE_STEAMWORKS)";
	}

	if ( descriptor->compiled && !descriptor->initialised ) {
		return "compatibility-only provider unavailable";
	}

	if ( descriptor->compiled ) {
		return "compatibility-only";
	}

	return "compatibility-unavailable";
}

/*
=============
QL_GetOnlineServicesModeLabel

Returns a high-level mode label summarising the current retained online-service
lane derived from the cached service table and build/runtime policy.
=============
*/
const char *QL_GetOnlineServicesModeLabel( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();
	const char *provider;

	if ( !services ) {
		return "Unavailable";
	}

	provider = services->auth.provider ? services->auth.provider : "";

	if ( strstr( provider, "QL_BUILD_ONLINE_SERVICES=0" ) != NULL ) {
		return "Build-disabled default (QL_BUILD_ONLINE_SERVICES=0)";
	}

	if ( strstr( provider, "QL_DISABLE_EXTERNAL_ECOSYSTEMS" ) != NULL ) {
		return "Externally-disabled compatibility lane";
	}

	if ( strstr( provider, "QL_DISABLE_STEAMWORKS" ) != NULL ) {
		return "Steamworks-disabled compatibility lane";
	}

#if QL_PLATFORM_BUILD_HYBRID
	return "Hybrid compatibility lane";
#elif QL_PLATFORM_HAS_STEAMWORKS
	return "Steamworks compatibility lane";
#elif QL_PLATFORM_HAS_OPEN_STEAM
	return "Open-adapter compatibility lane";
#else
	return "Unavailable";
#endif
}

/*
=============
QL_GetOnlineServicesPolicyLabel

Returns a high-level compatibility policy label summarising the current
online-service lane across the cached service table.
=============
*/
const char *QL_GetOnlineServicesPolicyLabel( void ) {
	const ql_platform_service_table *services = QL_GetPlatformServices();
	const char *authPolicy;

	if ( !services ) {
		return "compatibility-unavailable";
	}

	authPolicy = QL_DescribePlatformFeaturePolicy( &services->auth );

	if ( strstr( authPolicy, "compatibility-disabled" ) != NULL ) {
		return authPolicy;
	}

#if QL_PLATFORM_BUILD_HYBRID
	return "compatibility-opt-in heuristic hybrid";
#elif QL_PLATFORM_HAS_STEAMWORKS
	if ( services->auth.compiled && !services->auth.initialised ) {
		return "compatibility-opt-in heuristic steamworks (provider unavailable)";
	}

	return "compatibility-opt-in heuristic steamworks";
#elif QL_PLATFORM_HAS_OPEN_STEAM
	return "compatibility-opt-in heuristic open-adapter";
#else
	return authPolicy;
#endif
}

/*
=============
QL_GetOnlineServicesParityScopeLabel

Returns the explicit source-parity classification for the current online
service lane.
=============
*/
const char *QL_GetOnlineServicesParityScopeLabel( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	return "permanent-bounded-divergence";
#else
	const char *policyLabel = QL_GetOnlineServicesPolicyLabel();

	if ( strstr( policyLabel ? policyLabel : "", "compatibility-disabled" ) != NULL ) {
		return "runtime-disabled-bounded-divergence";
	}

#if QL_PLATFORM_BUILD_HYBRID
	return "opt-in-hybrid-compatibility";
#elif QL_PLATFORM_HAS_STEAMWORKS
	return "opt-in-steamworks-compatibility";
#elif QL_PLATFORM_HAS_OPEN_STEAM
	return "opt-in-open-adapter-compatibility";
#else
	return "compatibility-unavailable";
#endif
#endif
}

/*
=============
QL_GetOnlineServicesParityReasonLabel

Returns a stable human-readable reason explaining why the current online
service lane is or is not a default retail-equivalent source-parity target.
=============
*/
const char *QL_GetOnlineServicesParityReasonLabel( void ) {
#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	return "default builds keep Quake Live online services disabled until a documented open replacement exists";
#else
	const char *policyLabel = QL_GetOnlineServicesPolicyLabel();

	if ( strstr( policyLabel ? policyLabel : "", "compatibility-disabled" ) != NULL ) {
		if ( strstr( policyLabel, "QL_DISABLE_STEAMWORKS" ) != NULL ) {
			return "runtime policy disables the opted-in Steamworks compatibility lane";
		}

		return "runtime policy disables the opted-in online-service compatibility lane";
	}

	return "opt-in online-service providers remain bounded compatibility until validated against an open replacement";
#endif
}

#if QL_PLATFORM_HAS_STEAMWORKS
/*
=============
QL_PlatformSteamworks_InitCached

Attempts to initialise Steamworks, caching successful initialisation while
allowing failed launch-time attempts to recover once Steam becomes available.
=============
*/
static qboolean QL_PlatformSteamworks_InitCached( void ) {
	time_t now;

	if ( ql_platformSteamworksInitialised ) {
		return qtrue;
	}

	now = time( NULL );
	if ( ql_platformSteamworksNextAttemptTime && now != (time_t)-1 && now < ql_platformSteamworksNextAttemptTime ) {
		return qfalse;
	}

	ql_platformSteamworksInitialised = QL_Steamworks_Init();
	if ( ql_platformSteamworksInitialised ) {
		ql_platformSteamworksNextAttemptTime = 0;
		return qtrue;
	}

	if ( now != (time_t)-1 ) {
		ql_platformSteamworksNextAttemptTime = now + QL_STEAMWORKS_RETRY_SECONDS;
	}

	return qfalse;
}
#endif

/*
=============
QL_ResetPlatformServices

Clears cached platform-service descriptors and Steamworks retry state.
=============
*/
void QL_ResetPlatformServices( void ) {
	memset( &ql_platformServices, 0, sizeof( ql_platformServices ) );
	ql_platformServicesInitialised = qfalse;

#if QL_PLATFORM_HAS_STEAMWORKS
	ql_platformSteamworksInitialised = qfalse;
	ql_platformSteamworksNextAttemptTime = 0;
#endif
}

/*
=============
QL_BuildServiceTable

Constructs a service descriptor table based on build flags and runtime state.
=============
*/
static ql_platform_service_table QL_BuildServiceTable( void ) {
	ql_platform_service_table table;
	qboolean externalDisabled;
#if QL_PLATFORM_HAS_STEAMWORKS || QL_PLATFORM_HAS_OPEN_STEAM || QL_PLATFORM_BUILD_HYBRID
	const char *externalDisabledProvider;
#endif

	memset( &table, 0, sizeof( table ) );

#if !QL_PLATFORM_HAS_ONLINE_SERVICES
	table.auth.provider = "Build-disabled (QL_BUILD_ONLINE_SERVICES=0)";
	table.matchmaking.provider = "Build-disabled (QL_BUILD_ONLINE_SERVICES=0)";
	table.workshop.provider = "Build-disabled (QL_BUILD_ONLINE_SERVICES=0)";
	table.overlay.provider = "Build-disabled (QL_BUILD_ONLINE_SERVICES=0)";
	table.stats.provider = "Build-disabled (QL_BUILD_ONLINE_SERVICES=0)";

	QL_FinaliseDescriptor( &table.auth, "Unavailable" );
	QL_FinaliseDescriptor( &table.matchmaking, "Unavailable" );
	QL_FinaliseDescriptor( &table.workshop, "Unavailable" );
	QL_FinaliseDescriptor( &table.overlay, "Unavailable" );
	QL_FinaliseDescriptor( &table.stats, "Unavailable" );
	return table;
#endif

	externalDisabled = QL_PlatformExternalEcosystemsDisabled();

	if ( externalDisabled ) {
#if QL_PLATFORM_HAS_STEAMWORKS || QL_PLATFORM_HAS_OPEN_STEAM || QL_PLATFORM_BUILD_HYBRID
		externalDisabledProvider = QL_PlatformExternalEcosystemsDisableProviderLabel();

		table.auth.compiled = qtrue;
		table.auth.initialised = qfalse;
		table.auth.provider = externalDisabledProvider;

		table.matchmaking.compiled = qtrue;
		table.matchmaking.initialised = qfalse;
		table.matchmaking.provider = externalDisabledProvider;

		table.workshop.compiled = qtrue;
		table.workshop.initialised = qfalse;
		table.workshop.provider = externalDisabledProvider;

		table.overlay.compiled = qtrue;
		table.overlay.initialised = qfalse;
		table.overlay.provider = externalDisabledProvider;

		table.stats.compiled = qtrue;
		table.stats.initialised = qfalse;
		table.stats.provider = externalDisabledProvider;
#endif

		QL_FinaliseDescriptor( &table.auth, "Unavailable" );
		QL_FinaliseDescriptor( &table.matchmaking, "Unavailable" );
		QL_FinaliseDescriptor( &table.workshop, "Unavailable" );
		QL_FinaliseDescriptor( &table.overlay, "Unavailable" );
		QL_FinaliseDescriptor( &table.stats, "Unavailable" );
		return table;
	}

#if QL_PLATFORM_HAS_STEAMWORKS
	qboolean steamInitialised = QL_PlatformSteamworks_InitCached();
#endif

#if QL_PLATFORM_BUILD_HYBRID
	table.auth.compiled = qtrue;
	table.auth.initialised = qtrue;
	table.auth.provider = "Hybrid";
#elif QL_PLATFORM_HAS_STEAMWORKS
	table.auth.compiled = qtrue;
	table.auth.initialised = steamInitialised;
	table.auth.provider = "Steamworks";
#elif QL_PLATFORM_HAS_OPEN_STEAM
	table.auth.compiled = qtrue;
	table.auth.initialised = qtrue;
	table.auth.provider = "Open Steam Adapter";
#endif

#if QL_PLATFORM_HAS_STEAMWORKS
	table.matchmaking.compiled = qtrue;
	table.matchmaking.initialised = steamInitialised;
	table.matchmaking.provider = "Steamworks";
	table.workshop.compiled = qtrue;
	table.workshop.initialised = steamInitialised;
	table.workshop.provider = "Steam UGC";
	table.overlay.compiled = qtrue;
	table.overlay.initialised = steamInitialised;
	table.overlay.provider = "Steam Overlay";
	table.stats.compiled = qtrue;
	table.stats.initialised = steamInitialised;
	table.stats.provider = "Steam Stats";
#endif

#if QL_PLATFORM_HAS_OPEN_STEAM
	table.matchmaking.compiled = qtrue;
	table.matchmaking.initialised = qtrue;
	table.matchmaking.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steamworks + GameNetworkingSockets" : "GameNetworkingSockets";
	table.workshop.compiled = qtrue;
	table.workshop.initialised = qtrue;
	table.workshop.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steam UGC + REST Mirror" : "REST UGC Service";
	table.overlay.compiled = qtrue;
	table.overlay.initialised = qtrue;
	table.overlay.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steam Overlay + In-Process UI" : "In-Process UI Overlay";
	table.stats.compiled = qtrue;
	table.stats.initialised = qtrue;
	table.stats.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steam Stats + Metrics REST" : "Metrics REST Adapter";
#endif

	QL_FinaliseDescriptor( &table.auth, "Unavailable" );
	QL_FinaliseDescriptor( &table.matchmaking, "Unavailable" );
	QL_FinaliseDescriptor( &table.workshop, "Unavailable" );
	QL_FinaliseDescriptor( &table.overlay, "Unavailable" );
	QL_FinaliseDescriptor( &table.stats, "Unavailable" );

	return table;
}

/*
=============
QL_GetPlatformServices

Returns a cached snapshot of platform service descriptors.
=============
*/
const ql_platform_service_table *QL_GetPlatformServices( void ) {
	if ( !ql_platformServicesInitialised ) {
		ql_platformServices = QL_BuildServiceTable();
		ql_platformServicesInitialised = qtrue;
	}

	return &ql_platformServices;
}

/*
=============
QL_RefreshPlatformServices

Rebuilds the cached service descriptor table so opted-in platform integrations
can recover from launch-time unavailability.
=============
*/
const ql_platform_service_table *QL_RefreshPlatformServices( void ) {
	ql_platformServices = QL_BuildServiceTable();
	ql_platformServicesInitialised = qtrue;
	return &ql_platformServices;
}
