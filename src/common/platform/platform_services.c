#include "platform_services.h"

#include <string.h>

#include "platform_config.h"
static void QL_FinaliseDescriptor( ql_platform_feature_descriptor *descriptor, const char *fallbackLabel ) {
    if ( !descriptor ) {
        return;
    }

    if ( !descriptor->provider && fallbackLabel ) {
        descriptor->provider = fallbackLabel;
    }
}

static ql_platform_service_table QL_BuildServiceTable( void ) {
    ql_platform_service_table table;
    memset( &table, 0, sizeof( table ) );

#if QL_PLATFORM_BUILD_HYBRID
    table.auth.supported = qtrue;
    table.auth.provider = "Hybrid";
#elif QL_PLATFORM_HAS_STEAMWORKS
    table.auth.supported = qtrue;
    table.auth.provider = "Steamworks";
#elif QL_PLATFORM_HAS_OPEN_STEAM
    table.auth.supported = qtrue;
    table.auth.provider = "Open Steam Adapter";
#endif

#if QL_PLATFORM_HAS_STEAMWORKS
    table.matchmaking.supported = qtrue;
    table.matchmaking.provider = "Steamworks";
    table.workshop.supported = qtrue;
    table.workshop.provider = "Steam UGC";
    table.overlay.supported = qtrue;
    table.overlay.provider = "Steam Overlay";
    table.stats.supported = qtrue;
    table.stats.provider = "Steam Stats";
#endif

#if QL_PLATFORM_HAS_OPEN_STEAM
    table.matchmaking.supported = qtrue;
    table.matchmaking.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steamworks + GameNetworkingSockets" : "GameNetworkingSockets";
    table.workshop.supported = qtrue;
    table.workshop.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steam UGC + REST Mirror" : "REST UGC Service";
    table.overlay.supported = qtrue;
    table.overlay.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steam Overlay + In-Process UI" : "In-Process UI Overlay";
    table.stats.supported = qtrue;
    table.stats.provider = QL_PLATFORM_HAS_STEAMWORKS ? "Hybrid: Steam Stats + Metrics REST" : "Metrics REST Adapter";
#endif

    QL_FinaliseDescriptor( &table.matchmaking, "Unavailable" );
    QL_FinaliseDescriptor( &table.workshop, "Unavailable" );
    QL_FinaliseDescriptor( &table.overlay, "Unavailable" );
    QL_FinaliseDescriptor( &table.stats, "Unavailable" );

    if ( !table.auth.provider ) {
        table.auth.supported = qfalse;
        table.auth.provider = "Unavailable";
    }

    return table;
}

const ql_platform_service_table *QL_GetPlatformServices( void ) {
    static ql_platform_service_table table;
    static qboolean initialised = qfalse;

    if ( !initialised ) {
        table = QL_BuildServiceTable();
        initialised = qtrue;
    }

    return &table;
}
