#include "platform_services.h"

#include <stdlib.h>
#include <string.h>

#include "platform_config.h"
#if QL_PLATFORM_HAS_STEAMWORKS
#include "platform_steamworks.h"
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
QL_PlatformExternalEcosystemsDisabled

Checks whether runtime platform integrations should be disabled.
=============
*/
static qboolean QL_PlatformExternalEcosystemsDisabled( void ) {
	const char *flag;

	flag = getenv( "QL_DISABLE_EXTERNAL_ECOSYSTEMS" );
	if ( QL_StringRepresentsTrue( flag ) ) {
		return qtrue;
	}

	flag = getenv( "QL_DISABLE_STEAMWORKS" );
	return QL_StringRepresentsTrue( flag );
}

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

#if QL_PLATFORM_HAS_STEAMWORKS
/*
=============
QL_PlatformSteamworks_InitOnce

Attempts to initialise Steamworks a single time and returns the cached result.
=============
*/
static qboolean QL_PlatformSteamworks_InitOnce( void ) {
	static qboolean attempted = qfalse;
	static qboolean steamInitialised = qfalse;

	if ( !attempted ) {
		attempted = qtrue;
		steamInitialised = QL_Steamworks_Init();
	}

	return steamInitialised;
}
#endif

/*
=============
QL_BuildServiceTable

Constructs a service descriptor table based on build flags and runtime state.
=============
*/
static ql_platform_service_table QL_BuildServiceTable( void ) {
	ql_platform_service_table table;
	qboolean externalDisabled;

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
		table.auth.compiled = qtrue;
		table.auth.initialised = qfalse;
		table.auth.provider = "Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS";

		table.matchmaking.compiled = qtrue;
		table.matchmaking.initialised = qfalse;
		table.matchmaking.provider = "Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS";

		table.workshop.compiled = qtrue;
		table.workshop.initialised = qfalse;
		table.workshop.provider = "Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS";

		table.overlay.compiled = qtrue;
		table.overlay.initialised = qfalse;
		table.overlay.provider = "Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS";

		table.stats.compiled = qtrue;
		table.stats.initialised = qfalse;
		table.stats.provider = "Disabled by QL_DISABLE_EXTERNAL_ECOSYSTEMS";
#endif

		QL_FinaliseDescriptor( &table.auth, "Unavailable" );
		QL_FinaliseDescriptor( &table.matchmaking, "Unavailable" );
		QL_FinaliseDescriptor( &table.workshop, "Unavailable" );
		QL_FinaliseDescriptor( &table.overlay, "Unavailable" );
		QL_FinaliseDescriptor( &table.stats, "Unavailable" );
		return table;
	}

#if QL_PLATFORM_HAS_STEAMWORKS
	qboolean steamInitialised = QL_PlatformSteamworks_InitOnce();
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
	static ql_platform_service_table table;
	static qboolean initialised = qfalse;

	if ( !initialised ) {
		table = QL_BuildServiceTable();
		initialised = qtrue;
	}

	return &table;
}
