#include "platform_services.h"

#include <string.h>

#include "platform_config.h"
#if QL_PLATFORM_HAS_STEAMWORKS
#include "platform_steamworks.h"
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
	memset( &table, 0, sizeof( table ) );

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
